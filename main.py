from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
import uvicorn
from src.api.routers import teachers_router, tags_router, articles_router


def get_app() -> FastAPI:
    app = FastAPI()
    app.mount("/static", StaticFiles(directory="resources/static"), name="static")
    app.include_router(teachers_router)
    app.include_router(tags_router)
    app.include_router(articles_router)
    return app


app = get_app()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
