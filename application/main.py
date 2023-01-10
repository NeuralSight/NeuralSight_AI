"""
Imports the necessary modules from the FastAPI and Starlette libraries, as well as some custom modules from the "core.config", "endpoints", and "createsuperuser" modules.

Initializes an instance of the FastAPI class and sets some basic configuration options for the API, such as its title, OpenAPI endpoint, and a brief description.

Adds middleware for handling CORS (Cross-Origin Resource Sharing) requests, allowing requests from specific origins to access the API. The origins allowed are taken from the settings.BACKEND_CORS_ORIGINS configuration.

It creates a superuser using the createsuperuser_db() function, and also initializes the database using the db_initializer().

Defines an endpoint that redirects the client to the API documentation page.

Includes a router for the API's endpoints, prefixed with the "/v1" path.

Lastly the script is running the server using uvicorn library, It runs the "app" instance of the FastAPI.

"""


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


app.include_router(routers.api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    uvicorn.run("main:app")
