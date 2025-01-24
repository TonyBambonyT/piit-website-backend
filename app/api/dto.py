from datetime import datetime, date
from pydantic import BaseModel
from typing import List


class TeacherBase(BaseModel):
    """
    Базовая DTO-шка для модели Teacher.
    """
    academic_degree: str | None = None
    department_id: int
    department_leader: bool = False
    department_part_time_job_ids: List[int] = []
    department_secretary: bool = False
    firstname: str
    gender: str
    middlename: str | None = None
    person_id: int
    rank: str
    rank_short: str | None = None
    surname: str


class TeacherResponse(TeacherBase):
    """
    DTO для ответа с данными учителя (GET-запросы).
    """
    id: int


class TagBase(BaseModel):
    """
    Базовая DTO-шка для модели Tag
    """
    name: str


class ArticleBase(BaseModel):
    """
    Базовая DTO-шка для модели Article
    """
    icon: str
    title: str
    content: str
    tag_id: int
    event_date: date


class TagResponse(TagBase):
    """
    DTO-шка для получения всех тэгов
    """
    id: int


class ArticleResponse(ArticleBase):
    """
    DTO-шка для получения всех статей
    """
    id: int
    created_at: datetime
    views: int
    event_date: date


class ArticleLatestResponse(BaseModel):
    """
    DTO-шка для получения последних 6 статей
    """
    id: int
    icon: str
    title: str
    created_at: datetime
    event_date: date

