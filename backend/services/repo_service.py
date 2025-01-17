import logging
from typing import Dict, List, Set, Tuple, Optional

import aiohttp
from core.settings import settings
from db.abc_db import AbstractDatabase, AbstractRepoStorage
from db.postgres import PostgresRepoStorage, get_postgres
from enums.enums import GitHubUrls
from exceptions.repo_service_exceptions import RepoServiceExceptions
from fastapi import Depends

"""
Класс сервиса для работы с репозиториями.
Зависит от абстрактного хранилища данных, чтобы в будущем
иметь возможность использовать другую базу. 
Два основных метода это get_top100 и get_repo_info.

get_top100 выбирает данные из бд и возвращает их. 

get_repo_info отправляет запрос на апи гитхаба, чтобы получить
историю коммитов по конкретному репозиторию за конкретный период времени.
Токен гитхаба тут нужен, чтобы увеличить лимит запросов к апи и иметь возможность
парсить данные за большой промежуток времени (например, 1 год)
Остальные методы разделил по их назначению, чтобы не мешать всё в одну корзину.

Добавил несколько кастомных ошибок.

get_repo_service() возвращает экземпляр класса на основе нужного нам хранилища
"""


class RepoService:
    def __init__(
        self,
        storage_handler: AbstractRepoStorage,
        gh_auth_token: str = settings.gh_auth_token,
        gh_base_url: str = GitHubUrls.BASE_URL.value,
    ):
        self.storage_handler = storage_handler
        self.gh_auth_token = gh_auth_token
        self.gh_base_url = gh_base_url

    async def get_top100(self, sort_by: Optional[str] = None, sort_order: str = "asc") -> List[Dict]:
        try:
            return await self.storage_handler.get_top100(sort_by=sort_by, sort_order=sort_order)
        except Exception as e:
            logging.error(f"Error in get_top100: {e}")
            raise RepoServiceExceptions.InternalRepoServiceException()

    async def get_repo_info(
        self, owner: str, repo: str, since: str, until: str
    ) -> Dict:
        url = f"{self.gh_base_url}{owner}/{repo}/commits"
        params = {"since": since, "until": until, "per_page": 100}
        headers = {"Authorization": f"token {self.gh_auth_token}"}
        try:
            commits, authors = await self.fetch_commits(url, headers, params)
            return self.build_response(commits, authors, since, until)
        except RepoServiceExceptions.RepoServiceException as e:
            raise e
        except Exception as e:
            logging.error(f"Error in get_repo_info: {e}")
            raise RepoServiceExceptions.InternalRepoServiceException()

    async def fetch_commits(
        self, url: str, headers: dict, params: dict
    ) -> Tuple[int, Set[str]]:
        commits = 0
        authors = set()
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(url, headers=headers, params=params) as response:
                    await self.handle_rate_limit(response)
                    response.raise_for_status()
                    response_json = await response.json()
                    commits += len(response_json)
                    authors.update(self.extract_authors(response_json))
                    if len(response_json) < 100:
                        break
                    params["page"] = params.get("page", 1) + 1
        return commits, authors

    @staticmethod
    async def handle_rate_limit(response: aiohttp.ClientResponse):
        if (
            response.status == 403
            and "rate limit" in (await response.json()).get("message", "").lower()
        ):
            raise RepoServiceExceptions.RateLimitExceededException()

    @staticmethod
    def extract_authors(response_json: list) -> Set[str]:
        return {
            f"{commit_info['commit']['author']['name']} <{commit_info['commit']['author']['email']}>"
            for commit_info in response_json
        }

    @staticmethod
    def build_response(commits: int, authors: Set[str], since: str, until: str) -> Dict:
        return {
            "commits": commits,
            "authors": list(authors),
            "date": {"since": since, "until": until},
        }


def get_repo_service(
    db: AbstractDatabase = Depends(get_postgres),
) -> RepoService:
    storage = PostgresRepoStorage(db)
    return RepoService(storage)
