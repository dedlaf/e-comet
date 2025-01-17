from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from schemas.response_schemas import RepoActivityResponse, RepoResponse
from services.repo_service import RepoService, get_repo_service

router = APIRouter()


"""
Маршруты роутера, добавил схемы ответов, а также краткое описание эндпоинта.
Используют Depends для повышения переиспользования кода. Возвращают результат
работы RepoService
"""

@router.get(
    "/top100",
    response_model=List[RepoResponse],
    response_description="List of top 100 repositories",
)
async def get_top100(
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc or desc"),
    repo_service: RepoService = Depends(get_repo_service)
):
    return await repo_service.get_top100(sort_by=sort_by, sort_order=sort_order)



@router.get(
    "/{owner}/{repo}/activity",
    response_model=RepoActivityResponse,
    response_description="Repository activity details",
)
async def get_repo_info(
    owner: str,
    repo: str,
    since: str = Query(..., description="Start date in YYYY-MM-DD format"),
    until: str = Query(..., description="End date in YYYY-MM-DD format"),
    repo_service: RepoService = Depends(get_repo_service),
):
    return await repo_service.get_repo_info(owner, repo, since, until)
