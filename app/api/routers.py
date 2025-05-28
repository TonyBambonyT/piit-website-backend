from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Path, Form, UploadFile, Query, File
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dto import TeacherBase, TeacherResponse, TagResponse, TagBase, ArticleResponse, ArticleBase, \
    ArticleLatestResponse, CurriculumUnitResponse, SubjectResponse, StudGroupResponse, CurriculumUnitFullResponse, \
    TeacherWithPracticeResponse, SubjectWithPracticeResponse, AdminRegisterRequest
from app.config.config import settings
from app.providers import get_teacher_service, get_tag_service, get_article_service, get_curriculum_unit_service, \
    get_subject_service, get_stud_group_service, get_data_sync_manager, get_admin_user_service
from app.service.article_service import ArticleService
from app.service.auth_service import AdminUserService
from app.service.common.data_sync_manager import DataSyncManager
from app.service.common.utils import save_icon_file, create_access_token, admin_required
from app.service.cur_unit_service import CurriculumUnitService
from app.service.stud_group_service import StudGroupService
from app.service.subject_service import SubjectService
from app.service.tag_service import TagService
from app.service.teacher_service import TeacherService

teachers_router = APIRouter(prefix="/teachers", tags=["Teachers"])
articles_router = APIRouter(prefix="/articles", tags=["Articles"])
tags_router = APIRouter(prefix="/tags", tags=["Tags"])
cur_units_router = APIRouter(prefix="/units", tags=["Curriculum units"])
subjects_router = APIRouter(prefix="/subjects", tags=["Subjects"])
stud_groups_router = APIRouter(prefix="/groups", tags=["Student groups"])
sync_router = APIRouter(prefix="/sync", tags=["Synchronize"])
auth_router = APIRouter(prefix="/auth", tags=["Auth"])


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


@subjects_router.get(
    "/{teacher_id}/subjects",
    response_model=list[SubjectWithPracticeResponse],
    responses={
        200: {"description": "Предметы, которые преподаёт указанный преподаватель."},
        404: {"description": "Преподаватель или предметы не найдены."},
    },
)
def get_teacher_subjects(
        teacher_id: int,
        service: SubjectService = Depends(get_subject_service),
):
    """
    Возвращает список предметов, которые преподает указанный пропадаватель (по его ID)
    """
    subjects = service.get_subjects_by_teacher_id(teacher_id)
    if not subjects:
        raise HTTPException(status_code=404, detail=f"No subjects found for teacher {teacher_id}")
    return subjects


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
    "/{teacher_id}/icon",
    dependencies=[Depends(admin_required)],
    responses={
        200: {"description": "Иконка успешно загружена."},
        400: {"description": "Неверный тип файла."},
        404: {"description": "Преподаватель не найден."},
    },
)
def upload_teacher_icon(
        teacher_id: int = Path(..., title="ID преподавателя"),
        icon: UploadFile = File(...),
        service: TeacherService = Depends(get_teacher_service),
):
    """
    Загружает иконку преподавателю по его ID.
    """
    if not icon.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Expected an image.")
    teacher = service.get_teacher_by_id(teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail=f"Teacher with ID {teacher_id} not found")
    try:
        icon_path = save_icon_file(icon, prefix=f"teacher_{teacher_id}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    service.update_teacher_icon(teacher_id, icon_path)
    return {"message": "Icon uploaded successfully", "icon_path": icon_path}


@sync_router.post(
    "/teachers",
    responses={
        200: {"description": "Синхронизация завершена успешно."},
        500: {"description": "Ошибка синхронизации с внешним API."},
    },
)
def synchronize_teachers(service: TeacherService = Depends(get_teacher_service)):
    """
    Синхронизирует данные учителей из внешнего API с базой данных (без удаления старых данных).
    Ручка была сделана чисто для удобства и тестирования. Не используем в дальнейшем.
    """
    try:
        url = settings.TEACHERS_URI
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
        year_min: int | None = Query(None, description="Год с..."),
        year_max: int | None = Query(None, description="Год по..."),
        month_min: int | None = Query(None, description="Месяц с..."),
        month_max: int | None = Query(None, description="Месяц по..."),
        tags: list[str] | None = Query(None, description="Фильтр по тегам"),
        page: int = Query(1, description="Номер страницы"),
        limit: int = Query(12, description="Количество новостей на страницу"),
        service: ArticleService = Depends(get_article_service),
):
    if (month_min or month_max) and not (year_min or year_max):
        raise HTTPException(status_code=400,
                            detail="Фильтрация по месяцу возможна только при указании диапазона годов.")
    articles = service.get_filtered_articles(year_min, year_max, month_min, month_max, tags, page, limit)
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
    dependencies=[Depends(admin_required)],
    response_model=ArticleResponse,
    responses={
        201: {"description": "Статья успешно создана."},
        400: {"description": "Ошибка: статья с таким названием уже существует или файл имеет неправильный формат."},
    },
)
def create_article(
        icon: UploadFile | None = File(None),
        title: str = Form(...),
        content: str = Form(...),
        tag_ids: list[int] = Form(...),
        event_date: date = Form(...),
        service: ArticleService = Depends(get_article_service),
):
    """
    Создает новую статью.
    """
    if icon:
        if not icon.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Expected an image.")
        try:
            icon_path = save_icon_file(icon, prefix=title)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        icon_path = settings.DEFAULT_ARTICLE_ICON  # например: "/static/icons/default_article.png"
    article_data = ArticleBase(title=title, content=content, tag_ids=tag_ids, icon=icon_path, event_date=event_date)
    created_article = service.create_article(article_data)
    if not created_article:
        raise HTTPException(status_code=400, detail="Article with this title already exists")
    return created_article


@articles_router.put(
    "/{article_id}",
    dependencies=[Depends(admin_required)],
    response_model=ArticleResponse,
    responses={
        200: {"description": "Статья успешно обновлена."},
        404: {"description": "Статья не найдена."},
    },
)
def update_article(
        article_id: int,
        icon: UploadFile = File(None),
        title: str | None = Form(None),
        content: str | None = Form(None),
        tag_ids: list[int] = Form(None),
        event_date: str | None = Form(None),
        service: ArticleService = Depends(get_article_service)
):
    """
    Обновляет статью по ID. Все поля опциональны.
    """
    updated = service.update_article_with_optional_fields(
        article_id=article_id,
        icon=icon,
        title=title,
        content=content,
        tag_ids=tag_ids,
        event_date=event_date,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Article not found")
    return updated


@articles_router.delete(
    "/{article_id}",
    dependencies=[Depends(admin_required)],
    status_code=204,
    responses={
        204: {"description": "Статья успешно удалена."},
        404: {"description": "Статья не найдена."},
    },
)
def delete_article(
        article_id: int,
        service: ArticleService = Depends(get_article_service)
):
    """
    Удаляет статью по id.
    """
    success = service.delete_article(article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")


@cur_units_router.get(
    "/",
    response_model=list[CurriculumUnitResponse],
    responses={
        200: {"description": "Список единиц учебного плана."},
        404: {"description": "Единицы учебного плана не найдены."},
    },
)
def get_all_curriculum_units(service: CurriculumUnitService = Depends(get_curriculum_unit_service)):
    """
    Возвращает список всех единиц учебного плана.
    """
    units = service.get_all_curriculum_units()
    if not units:
        raise HTTPException(status_code=404, detail="No curriculum units found")
    return units


@sync_router.post(
    "/units",
    responses={
        201: {"description": "Единицы учебного плана успешно сохранены."},
        400: {"description": "Ошибка сохранения единиц учебного плана."},
    },
)
def update_curriculum_units(service: CurriculumUnitService = Depends(get_curriculum_unit_service)):
    """
    Обновляет учебные единицы, загружая данные с внешнего API (без удаления старых данных).
    Ручка была сделана чисто для удобства и тестирования. Не используем в дальнейшем.
    """
    try:
        url = settings.CUR_UNITS_URI
        service.create_curriculum_units(url)
        return {"message": "Curriculum_units added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@subjects_router.get(
    "/",
    response_model=list[SubjectResponse],
    responses={
        200: {"description": "Список предметов."},
        404: {"description": "Предметы не найдены."},
    },
)
def get_all_subjects(service: SubjectService = Depends(get_subject_service)):
    """
    Возвращает список всех предметов.
    """
    subjects = service.get_all_subjects()
    if not subjects:
        raise HTTPException(status_code=404, detail="No subjects found")
    return subjects


@sync_router.post(
    "/subjects",
    responses={
        201: {"description": "Предметы успешно добавлены."},
        400: {"description": "Ошибка добавления предметов."},
    },
)
def update_subjects(service: SubjectService = Depends(get_subject_service)):
    """
    Обновляет список предметов из БРС (без удаления старых данных).
    Ручка была сделана чисто для удобства и тестирования. Не используем в дальнейшем.
    """
    try:
        url = settings.SUBJECTS_URI
        service.create_subjects(url)
        return {"message": "Subjects added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@teachers_router.get(
    "/{subject_id}/teachers",
    response_model=list[TeacherWithPracticeResponse],
    responses={
        200: {"description": "Список преподавателей, ведущих предмет."},
        404: {"description": "Преподаватели не найдены для указанного предмета."},
    },
)
def get_teachers_by_subject(
        subject_id: int,
        service: TeacherService = Depends(get_teacher_service)
):
    """
    Возвращает список преподавателей, преподающих указанный предмет.
    """
    teachers = service.get_teachers_by_subject_id(subject_id)
    if not teachers:
        raise HTTPException(status_code=404, detail=f"No teachers found for subject {subject_id}")
    return teachers


@stud_groups_router.get(
    "/",
    response_model=list[StudGroupResponse],
    responses={
        200: {"description": "Список групп."},
        404: {"description": "Группы не найдены."},
    },
)
def get_all_stud_groups(service: StudGroupService = Depends(get_stud_group_service)):
    """
    Возвращает список всех групп.
    """
    groups = service.get_all_stud_groups()
    if not groups:
        raise HTTPException(status_code=404, detail="No stud groups found")
    return groups


@sync_router.post(
    "/groups",
    responses={
        201: {"description": "Группы успешно добавлены."},
        400: {"description": "Ошибка добавления групп."},
    },
)
def update_stud_groups(service: StudGroupService = Depends(get_stud_group_service)):
    """
    Обновляет список студенческих групп из БРС (без удаления старых данных).
    Ручка была сделана чисто для удобства и тестирования. Не используем в дальнейшем.
    """
    try:
        url = settings.STUB_GROUPS_URI
        service.create_stud_groups(url)
        return {"message": "Student groups added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@sync_router.post(
    "/all",
    dependencies=[Depends(admin_required)],
    responses={
        200: {"description": "Полная синхронизация завершена."},
        500: {"description": "Ошибка во время полной синхронизации."}
    }
)
def sync_all(service: DataSyncManager = Depends(get_data_sync_manager)):
    """
    Полностью синхронизирует все данные с БРС: преподаватели, предметы, группы, учебные единицы (удаляя старые данные).
    Данную ручку мы используем для кнопки в дальнейшем!!
    """
    try:
        service.sync_all()
        return {"message": "Information updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@cur_units_router.get(
    "/full",
    response_model=list[CurriculumUnitFullResponse],
    responses={200: {"description": "Список всех учебных единиц с полной информацией."}},
)
def get_all_full_curriculum_units(service: CurriculumUnitService = Depends(get_curriculum_unit_service)):
    """
    Возвращает список всех учебных единиц с полной информацией.
    """
    return service.get_all_full_curriculum_units()


@cur_units_router.get(
    "/brs/{brs_id}",
    response_model=CurriculumUnitResponse,
    responses={
        200: {"description": "Учебная единица успешно найдена."},
        404: {"description": "Учебная единица с таким BRS ID не найдена."},
    },
)
def get_curriculum_unit_by_brs_id(
        brs_id: int,
        service: CurriculumUnitService = Depends(get_curriculum_unit_service)
):
    """
    Получает одну учебную единицу по её BRS ID.
    """
    unit = service.get_curriculum_unit_by_brs_id(brs_id)
    if not unit:
        raise HTTPException(status_code=404, detail=f"Curriculum unit with brs_id={brs_id} not found")
    return unit


@cur_units_router.get(
    "/full/{id}",
    response_model=CurriculumUnitFullResponse,
    responses={
        200: {"description": "Полная информация об учебной единице успешно найдена."},
        404: {"description": "Учебная единица с таким ID не найдена."},
    },
)
def get_full_curriculum_unit_by_id(
        id: int,
        service: CurriculumUnitService = Depends(get_curriculum_unit_service)
):
    """
    Получает одну учебную единицу с полной информацией по её ID в нашей базе.
    """
    unit = service.get_full_curriculum_unit_info_by_id(id)
    if not unit:
        raise HTTPException(status_code=404, detail=f"Curriculum unit with id={id} not found")
    return unit


@cur_units_router.get(
    "/full/brs/{brs_id}",
    response_model=CurriculumUnitFullResponse,
    responses={
        200: {"description": "Полная информация об учебной единице по BRS ID."},
        404: {"description": "Учебная единица с таким BRS ID не найдена."},
    },
)
def get_full_curriculum_unit_by_brs_id(
        brs_id: int,
        service: CurriculumUnitService = Depends(get_curriculum_unit_service)
):
    """
    Получает одну учебную единицу с полной информацией по её BRS ID.
    """
    unit = service.get_full_curriculum_unit_info_by_brs_id(brs_id)
    if not unit:
        raise HTTPException(status_code=404, detail=f"Curriculum unit with brs_id={brs_id} not found")
    return unit


@auth_router.post(
    "/register",
    summary="Регистрация администратора",
    description="Создаёт нового администратора с логином и паролем.",
    responses={
        200: {"description": "Администратор успешно зарегистрирован"},
        400: {"description": "Пользователь уже существует"}
    }
)
def register_admin(
        request: AdminRegisterRequest,
        service: AdminUserService = Depends(get_admin_user_service)
):
    try:
        user = service.register_admin(request)
        return {"message": f"Admin {user.username} created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post(
    "/login",
    summary="Вход администратора",
    description="Принимает логин и пароль администратора и возвращает JWT токен.",
    response_model=dict,
    responses={
        200: {"description": "Успешный вход. Возвращает токен."},
        401: {"description": "Неверные учётные данные"}
    }
)
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        service: AdminUserService = Depends(get_admin_user_service)
):
    user = service.validate_credentials(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
