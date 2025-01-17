from abc import ABC, abstractmethod
from typing import Dict, List

from psycopg2.extensions import connection

"""
Абстрактные классы для более гибкой работы с базами.

AbstractDatabase нужен для подключения к базе.

AbstractRepoStorage нужен для реализации работы c таблицей,
где хранятся именно репозитории.

Эти два класса гарантируют, что в случае изменения и/или добавления
нового хранилища, в других частях кода оно будет подключаться и работать,
так же, как и текущее и нам не придется менять классы сервисов(например, RepoService)
"""


class AbstractDatabase(ABC):
    @abstractmethod
    def get_connection(self) -> connection:
        pass


class AbstractRepoStorage(ABC):
    @abstractmethod
    async def get_top100(self) -> List[Dict]:
        pass
