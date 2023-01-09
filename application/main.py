from fastapi import FastAPI  # File, Response, UploadFile
from starlette.middleware.cors import CORSMiddleware
from core.config import settings
from endpoints import routers
from starlette.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from typing import Any


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="""## NeuralSight API""",
)
# app.mount("/runs", StaticFiles(directory="runs", html=True), name="runs")

# setup cors
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# get the details to create super user
from createsuperuser import main as createsuperuser_db
from db_starter import main as db_initializer

# initializing DATABASE
db_initializer()
print("DB Initialized well")
# create super user
createsuperuser_db()
print("Super User Init well")


@app.get("/", tags=["Redirect"])
def redirect_to_docs() -> Any:
    return RedirectResponse(url="redoc")


app.include_router(routers.api_router, prefix="/v1")#settings.API_V1_STR)


if __name__ == "__main__":
    uvicorn.run("main:app")
