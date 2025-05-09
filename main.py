from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
import uvicorn
from app.api.routers import teachers_router, tags_router, articles_router, cur_units_router, subjects_router, \
    stud_groups_router, sync_router, auth_router
from app.service.common.scheduler import create_scheduler


def get_app() -> FastAPI:
    scheduler = create_scheduler()

    async def on_startup():
        scheduler.start()

    async def on_shutdown():
        scheduler.shutdown(wait=True)

    app = FastAPI(
        on_startup=[on_startup],
        on_shutdown=[on_shutdown]
    )
    app.include_router(teachers_router)
    app.include_router(tags_router)
    app.include_router(articles_router)
    app.include_router(cur_units_router)
    app.include_router(subjects_router)
    app.include_router(stud_groups_router)
    app.include_router(sync_router)
    app.include_router(auth_router)
    app.mount("/static", StaticFiles(directory="resources/static"), name="static")
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
