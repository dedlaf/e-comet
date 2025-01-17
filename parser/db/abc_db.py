from abc import ABC, abstractmethod


"""
Абстрактный класс, который гарантирует наличие необходимых методов,
в случае, если мы захотим изменить и/или добавить ещё одну бд. Это
повышает переиспользуемость кода, а также локализует возможные ошибки. 
"""


class StorageHandler(ABC):
    @abstractmethod
    def upsert_repo(self, item):
        pass

    @abstractmethod
    def update_positions(self):
        pass

    @abstractmethod
    def execute_query(self, query, params):
        pass

    @abstractmethod
    def execute_update(self, query, params):
        pass

    @abstractmethod
    def execute(self, query, params):
        pass
