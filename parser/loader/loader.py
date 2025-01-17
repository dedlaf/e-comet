import logging

from db.abc_db import StorageHandler
from enums.enums import SQLQueries
from more_itertools import chunked

"""
Класс для загрузки данных в базу. Зависит от абстрактного хранилища,
чтобы в будущем было удобно сменить хранилище, в случае чего-либо.

Ключевой аспект здесь это вставка данных.
К сожалению, в т/з не было указано о наличии каких-либо индексов.
Поэтому для избежания дублирования приходится использовать костыль,
который смльно увеличивает количество запросов к базе.
Сначала обновляет данные, а потом уже вставляет,
в случае, если данных для обновления нет.
При наличии индекса по имени
репозиториев такой костыль можно было избежать и загружать данные батчами,
используя on conflict в запросе.
"""


class Loader:
    def __init__(
        self, storage_handler: StorageHandler, batch_size=20, sql_queries=SQLQueries
    ) -> None:
        self.storage_handler = storage_handler
        self.batch_size = batch_size
        self.sql_queries = sql_queries

    @staticmethod
    def transform_data(data: dict) -> list:
        try:
            return [
                (
                    item["full_name"],
                    item["owner"]["login"],
                    item["stargazers_count"],
                    item["watchers_count"],
                    item["forks_count"],
                    item["open_issues_count"],
                    item["language"],
                    0,
                    0,
                )
                for item in data["items"]
            ]
        except KeyError as e:
            logging.error(f"Key error during data transformation: {e}")
            raise
        except Exception as e:
            logging.error(
                f"An unexpected error occurred during data transformation: {e}"
            )
            raise

    def process_batch(self, batch: list):
        for item in batch:
            try:
                rowcount = self.storage_handler.execute_update(
                    self.sql_queries.UPDATE_REPO.value,
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

                if rowcount == 0:
                    self.storage_handler.execute(
                        self.sql_queries.INSERT_REPO.value, (*item,)
                    )
            except Exception as e:
                logging.error(f"Error during batch processing: {e}")
                raise

    def update_positions(self):
        try:
            self.storage_handler.execute(self.sql_queries.UPDATE_POSITIONS.value, ())
        except Exception as e:
            logging.error(f"Error during update_positions operation: {e}")
            raise

    def process_data(self, data: list):
        try:
            for batch in chunked(data, self.batch_size):
                self.process_batch(batch)
            self.update_positions()
        except Exception as e:
            logging.error(f"Error during data processing: {e}")
            raise
