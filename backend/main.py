from contextlib import asynccontextmanager

from api.v1 import repos
from core.settings import settings
from db.postgres import postgres_instance
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

"""
Точка входа бекенда. Использовал лайфспан для удобного подключения к бд.
Также разделил приложение на роутеры, чтобы было удобнее ставить 
базовый адрес, а также тег к каждому роутеру. Полезно, если потребуется
добавить другие маршруты с другим функционалом.
"""


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        yield
    finally:
        postgres_instance.close_all_connections()

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(repos.router, prefix="/api/repos", tags=["repos"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080)
