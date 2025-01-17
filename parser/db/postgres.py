import logging

import backoff
from core.settings import settings
from db.abc_db import StorageHandler
from enums.enums import SQLQueries
from psycopg2 import DatabaseError, InterfaceError, OperationalError, connect

"""
Выглядит страшно, но на самом деле логика довольно простая.
Основная фишка, это переподключение к базе, в случае её падения на некоторое время.
Это делает код отказоустойчивым, а также гарантирует выполнение вставки/обновления
в случае падения базы на короткий промежуток времени. Также предусмотрена обработка
различных видов ошибок.
"""


class PostgresHandler(StorageHandler):
    def __init__(self, sql_queries=SQLQueries) -> None:
        self.db = self.__get_postgres()
        self.sql_queries = sql_queries

    @backoff.on_exception(backoff.expo, OperationalError, max_tries=10, max_time=60)
    def __get_postgres(self):
        return connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_pass,
            database=settings.db_name,
        )

    def __execute_query(self, query, params):
        with self.db.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
            self.db.commit()
            return result

    def __execute_update(self, query, params):
        with self.db.cursor() as cursor:
            cursor.execute(query, params)
            rowcount = cursor.rowcount
            self.db.commit()
            return rowcount

    def __execute_simple(self, query, params):
        with self.db.cursor() as cursor:
            cursor.execute(query, params)
            self.db.commit()

    def __reconnect(self):
        logging.info("Reconnecting to the database...")
        self.db.close()
        self.db = self.__get_postgres()
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
            self.db.rollback()
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            self.db.rollback()
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
