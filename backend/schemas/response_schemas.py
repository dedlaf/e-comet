from datetime import date
from typing import List

from pydantic import BaseModel

"""
Схемы ответов эндпоинтов. Позволяют валидировать данные, а также
явно указывают, что эндпоинт отдаст по запросу
"""


class RepoResponse(BaseModel):
    repo: str
    owner: str
    position_cur: int
    position_prev: int
    stars: int
    watchers: int
    forks: int
    open_issues: int
    language: str


class DateRange(BaseModel):
    since: date
    until: date


class RepoActivityResponse(BaseModel):
    date: DateRange
    commits: int
    authors: List[str]
