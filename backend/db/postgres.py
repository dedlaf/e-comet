import logging
from typing import Dict, List, Optional

import backoff
from core.settings import settings
from db.abc_db import AbstractDatabase, AbstractRepoStorage
from enums.enums import SqlQueries
from psycopg2 import OperationalError, connect
from psycopg2.extensions import connection


"""
Два класса для работы с бд. Оба наследуются от своих абстрактных классов

PostgresDatabase выполняет подключение к постгрес, а также
обеспечивает переподключение в случае падения.

PostgresRepoStorage работает с таблицей, где лежат репозитории,
делает выборку топ100 репозиториев и возвращает их.

get_postgres_connection() возвращает новое подключение к бд
get_postgres() возвращает текущее подключение к бд
"""


class PostgresDatabase(AbstractDatabase):
    def __init__(self):
        self._connection: Optional[connection] = None

    @backoff.on_exception(backoff.expo, OperationalError, max_tries=5)
    def connect_to_db(self):
        self._connection = connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_pass,
            database=settings.db_name,
        )

    def get_connection(self) -> connection:
        if self._connection is None or self._connection.closed:
            self.connect_to_db()
        return self._connection

    def close_connection(self):
        if self._connection is not None:
            self._connection.close()


class PostgresRepoStorage(AbstractRepoStorage):
    def __init__(self, db: AbstractDatabase):
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


postgres_instance = PostgresDatabase()


def get_postgres_connection() -> AbstractDatabase:
    return PostgresDatabase()


def get_postgres() -> AbstractDatabase:
    return postgres_instance
