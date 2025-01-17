import logging
from typing import Dict, List

from core.settings import settings
from db.abc_db import AbstractDatabase, AbstractRepoStorage
from enums.enums import SqlQueries
from psycopg2 import OperationalError, pool


"""
Два класса для работы с бд. Оба наследуются от своих абстрактных классов

PostgresDatabase выполняет подключение к постгрес

PostgresRepoStorage работает с таблицей, где лежат репозитории,
делает выборку топ100 репозиториев и возвращает их.

"""


class PostgresDatabase(AbstractDatabase):
    def __init__(self):
        self._db_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            user=settings.db_user,
            password=settings.db_pass,
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name
        )

    def get_connection(self):
        return self._db_pool.getconn()

    def put_connection(self, conn):
        self._db_pool.putconn(conn)

    def close_all_connections(self):
        self._db_pool.closeall()


class PostgresRepoStorage(AbstractRepoStorage):
    def __init__(self, db: PostgresDatabase):
        self._db = db
        self.sql_queries = SqlQueries

    async def get_top100(self) -> List[Dict]:
        connection = self._db.get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(self.sql_queries.GET_TOP100.value)
            repositories = cursor.fetchall()
            cursor.close()
            return [
                {
                    "repo": repo_data[0],
                    "owner": repo_data[1],
                    "position_cur": repo_data[2],
                    "position_prev": repo_data[3],
                    "stars": repo_data[4],
                    "watchers": repo_data[5],
                    "forks": repo_data[6],
                    "open_issues": repo_data[7],
                    "language": repo_data[8] or "Unknown",
                }
                for repo_data in repositories
            ]
        except Exception as e:
            logging.error(f"Error in get_top100: {e}")
            raise
        finally:
            self._db.put_connection(connection)


postgres_instance = PostgresDatabase()


def get_postgres() -> AbstractDatabase:
    return postgres_instance
