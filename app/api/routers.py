import os
import shutil
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Path, Form, UploadFile, Query
from app.api.dto import TeacherBase, TeacherResponse, TagResponse, TagBase, ArticleResponse, ArticleBase, \
    ArticleLatestResponse
from app.config.config import settings
from app.providers import get_teacher_service, get_tag_service, get_article_service
from app.service.article_service import ArticleService
from app.service.tag_service import TagService
from app.service.teacher_service import TeacherService

teachers_router = APIRouter(prefix="/teachers", tags=["Teachers"])
articles_router = APIRouter(prefix="/articles", tags=["Articles"])
tags_router = APIRouter(prefix="/tags", tags=["Tags"])


@teachers_router.get(
    "/",
    response_model=list[TeacherResponse],
    responses={
        200: {"description": "Успешный ответ. Возвращает список преподавателей."},
        404: {"description": "Преподаватели не найдены."},
    },
)
def get_all_teachers(service: TeacherService = Depends(get_teacher_service)):
    """
    Возвращает список всех преподавателей.
    """
    teachers = service.get_all_teachers()
    if not teachers:
        raise HTTPException(status_code=404, detail="No teachers found")
    return teachers


@teachers_router.get(
    "/{teacher_id}",
    response_model=TeacherResponse,
    responses={
        200: {"description": "Успешный ответ. Возвращает информацию о преподавателе."},
        404: {"description": "Преподаватель с указанным ID не найден."},
    },
)
def get_teacher_by_id(
        teacher_id: int = Path(..., title="ID учителя", description="Уникальный id"),
        service: TeacherService = Depends(get_teacher_service),
):
    """
    Возвращает информацию о преподавателе по указанному id.
    """
    teacher = service.get_teacher_by_id(teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail=f"Teacher with ID {teacher_id} not found")
    return teacher


@teachers_router.post(
    "/",
    response_model=TeacherResponse,
    responses={
        201: {"description": "Преподаватель успешно создан."},
        400: {"description": "Ошибка создания: преподаватель уже существует."},
    },
)
def create_teacher(teacher: TeacherBase, service: TeacherService = Depends(get_teacher_service)):
    """
    Создает нового преподавателя.
    """
    created_teacher = service.create_teacher(teacher)
    if not created_teacher:
        raise HTTPException(status_code=400, detail="Teacher with this person_id already exists")
    return created_teacher


@teachers_router.post(
    "/synchronize",
    responses={
        200: {"description": "Синхронизация завершена успешно."},
        500: {"description": "Ошибка синхронизации с внешним API."},
    },
)
def synchronize_teachers(service: TeacherService = Depends(get_teacher_service)):
    """
    Синхронизирует данные учителей из внешнего API с базой данных.
    """
    try:
        url = settings.BRS_URI
        teachers = service.fetch_teachers_from_api(url)
        service.synchronize_teachers(teachers)
        return {"message": "Teachers synchronized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@tags_router.get(
    "/",
    response_model=list[TagResponse],
    responses={
        200: {"description": "Успешный ответ. Возвращает список тегов."},
        404: {"description": "Теги не найдены."},
    },
)
def get_all_tags(service: TagService = Depends(get_tag_service)):
    """
    Возвращает список всех тегов.
    """
    tags = service.get_all_tags()
    if not tags:
        raise HTTPException(status_code=404, detail="No tags found")
    return tags


@tags_router.post(
    "/",
    response_model=TagResponse,
    responses={
        201: {"description": "Тег успешно создан."},
        400: {"description": "Ошибка создания: такой тег уже существует."},
    },
)
def create_tag(tag: TagBase, service: TagService = Depends(get_tag_service)):
    """
    Создает новый тег.
    """
    created_tag = service.create_tag(tag)
    if not created_tag:
        raise HTTPException(status_code=400, detail="This tag already exists")
    return created_tag


@articles_router.get(
    "/",
    response_model=list[ArticleResponse],
    responses={
        200: {"description": "Успешный ответ. Возвращает список статей."},
        400: {"description": "Ошибка валидации. Например, если указан месяц без года."}
    },
)
def get_all_articles(
        year: int | None = Query(None, description="Фильтр по году"),
        month: int | None = Query(None, description="Фильтр по месяцу"),
        tags: list[str] | None = Query(None, description="Фильтр по тегам"),
        page: int = Query(1, description="Номер страницы"),
        limit: int = Query(12, description="Количество новостей на страницу"),
        service: ArticleService = Depends(get_article_service),
):
    """
    Возвращает список всех статей с возможностью фильтрации по году, месяцу и тегам.
    Поддерживает пагинацию (по 12 новостей на страницу).
    """
    if month and not year:
        raise HTTPException(status_code=400, detail="Фильтрация по месяцу доступна только при указании года.")
    articles = service.get_filtered_articles(year, month, tags, page, limit)
    if not articles:
        return []
    return articles


@articles_router.get(
    "/latest",
    response_model=list[ArticleLatestResponse],
    responses={
        200: {"description": "Успешный ответ. Возвращает 6 последних статей."}
    },
)
def get_latest_articles(service: ArticleService = Depends(get_article_service)):
    """
    Возвращает 6 последних статей, отсортированных по дате создания от новых к старым.
    """
    articles = service.get_latest_articles()
    if not articles:
        return []
    return articles


@articles_router.get(
    "/{article_id}",
    response_model=ArticleResponse,
    responses={
        200: {"description": "Успешный ответ. Возвращает статью."},
        404: {"description": "Статья не найдена."}
    },
)
def get_article_by_id(
        article_id: int = Path(..., title="ID статьи", description="Уникальный id"),
        service: ArticleService = Depends(get_article_service),
):
    """
    Возвращает статью по переданному id.
    """
    article = service.get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="No articles found")
    return article


@articles_router.post(
    "/",
    response_model=ArticleResponse,
    responses={
        201: {"description": "Статья успешно создана."},
        400: {"description": "Ошибка: статья с таким названием уже существует или файл имеет неправильный формат."},
    },
)
def create_article(
        icon: UploadFile,
        title: str = Form(...),
        content: str = Form(...),
        tag_id: int = Form(...),
        event_date: date = Form(...),
        service: ArticleService = Depends(get_article_service),
):
    """
    Создает новую статью.
    """
    if not icon.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Expected an image.")

    filename = f"{title.replace(' ', '_')}_{icon.filename}"
    icon_path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(icon_path, "wb") as buffer:
        shutil.copyfileobj(icon.file, buffer)

    icon_path = f"/static/icons/{filename}"
    article_data = ArticleBase(title=title, content=content, tag_id=tag_id, icon=icon_path, event_date=event_date)
    created_article = service.create_article(article_data)
    if not created_article:
        raise HTTPException(status_code=400, detail="Article with this title already exists")
    return created_article
