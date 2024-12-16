from fastapi import FastAPI
from src.api.routers import router as teachers_router
import uvicorn


def get_app() -> FastAPI:
    app = FastAPI()
    app.include_router(teachers_router, prefix="/teachers")
    return app


app = get_app()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
