import logging

import backoff
from core.settings import settings
from db.abc_db import StorageHandler
from enums.enums import SQLQueries
from psycopg2 import DatabaseError, InterfaceError, OperationalError, pool

"""
Выглядит страшно, но на самом деле логика довольно простая.
Основная фишка, это переподключение к базе, в случае её падения на некоторое время.
Это делает код отказоустойчивым, а также гарантирует выполнение вставки/обновления
в случае падения базы на короткий промежуток времени. Также предусмотрена обработка
различных видов ошибок.
"""


class PostgresHandler(StorageHandler):
    def __init__(self, sql_queries=SQLQueries) -> None:
        self.__create_connection_pool()
        self.sql_queries = sql_queries

    def __create_connection_pool(self):
        self.db_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            user=settings.db_user,
            password=settings.db_pass,
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name
        )

    @backoff.on_exception(backoff.expo, OperationalError, max_tries=10, max_time=60)
    def __get_postgres(self):
        if self.db_pool.closed:
            self.__create_connection_pool()
        return self.db_pool.getconn()

    def __execute_query(self, query, params):
        conn = self.__get_postgres()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                conn.commit()
            return result
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            raise
        finally:
            self.db_pool.putconn(conn)

    def __execute_update(self, query, params):
        conn = self.__get_postgres()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                rowcount = cursor.rowcount
                conn.commit()
            return rowcount
        except Exception as e:
            logging.error(f"Error executing update: {e}")
            raise
        finally:
            self.db_pool.putconn(conn)

    def __execute_simple(self, query, params):
        conn = self.__get_postgres()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
        except Exception as e:
            logging.error(f"Error executing statement: {e}")
            raise
        finally:
            self.db_pool.putconn(conn)

    def __reconnect(self):
        logging.info("Reconnecting to the database...")
        self.db_pool.closeall()
        self.__create_connection_pool()
        logging.info("Reconnection successful.")

    def _execute_with_reconnect(self, func, query, params):
        try:
            return func(query, params)
        except (InterfaceError, OperationalError) as e:
            logging.error(f"Connection error occurred: {e}")
            self.__reconnect()
            try:
                return func(query, params)
            except Exception as e:
                logging.error(f"Error during retry after reconnect: {e}")
                raise
        except DatabaseError as db_error:
            logging.error(f"Database error occurred: {db_error}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise

    @backoff.on_exception(backoff.expo, (InterfaceError, OperationalError), max_tries=5)
    def execute_query(self, query, params):
        return self._execute_with_reconnect(self.__execute_query, query, params)

    @backoff.on_exception(backoff.expo, (InterfaceError, OperationalError), max_tries=5)
    def execute_update(self, query, params):
        return self._execute_with_reconnect(self.__execute_update, query, params)

    @backoff.on_exception(backoff.expo, (InterfaceError, OperationalError), max_tries=5)
    def execute(self, query, params):
        self._execute_with_reconnect(self.__execute_simple, query, params)

    def upsert_repo(self, item):
        update_query = self.sql_queries.UPDATE_REPO.value
        insert_query = self.sql_queries.INSERT_REPO.value
        if (
            self.execute_update(
                update_query,
                (
                    item[1],
                    item[2],
                    item[3],
                    item[4],
                    item[5],
                    item[6],
                    item[8],
                    item[0],
                ),
            )
            == 0
        ):
            self.execute(insert_query, (*item,))

    def update_positions(self):
        self.execute(self.sql_queries.UPDATE_POSITIONS.value, ())
