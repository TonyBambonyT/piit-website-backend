from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
import uvicorn
from app.api.routers import teachers_router, tags_router, articles_router


def get_app() -> FastAPI:
    app = FastAPI()
    app.mount("/static", StaticFiles(directory="resources/static"), name="static")
    app.include_router(teachers_router)
    app.include_router(tags_router)
    app.include_router(articles_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = get_app()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
