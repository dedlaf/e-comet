from enums.enums import GitHubURL
from requests import get

"""
Можно было и не создавать этот класс, а оставить только функцию.
Тем не менее, возможно, в будущем эти данные надо будет как-то 
трансформировать или добавить другой функционал,
поэтому выделил под это отдельный класс
"""


class Fetcher:
    @staticmethod
    def fetch_repositories() -> dict:
        response = get(GitHubURL.REPOS_URL.value)
        return response.json()
