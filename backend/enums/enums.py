from enum import Enum

""""
Энамы, чтобы мы могли быть уверены, в корректности
запросов, а также, чтобы менять их в одном месте, вместо
изменения в других файлах
"""


class SqlQueries(str, Enum):

    GET_TOP100 = """
                    SELECT * FROM top100
                    ORDER BY stars DESC
                    LIMIT 100
                 """


class GitHubUrls(str, Enum):

    BASE_URL = "https://api.github.com/repos/"
