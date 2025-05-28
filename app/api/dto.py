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
    brs_id: int


class TeacherResponse(TeacherBase):
    """
    DTO для ответа с данными учителя (GET-запросы).
    """
    id: int
    icon: str


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
    tag_ids: list[int]
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


class CurriculumUnitResponse(BaseModel):
    id: int
    practice_teacher_brs_ids: list[int]
    stud_group_brs_id: int
    teacher_brs_id: int
    subject_brs_id: int
    brs_id: int


class SubjectResponse(BaseModel):
    id: int
    brs_id: int
    name: str


class StudGroupResponse(BaseModel):
    id: int
    brs_id: int
    course: int
    semester: int
    education_level: str


class CurriculumUnitFullResponse(BaseModel):
    id: int
    brs_id: int
    practice_teachers: list[TeacherResponse]
    teacher: TeacherResponse
    subject: SubjectResponse
    stud_group: StudGroupResponse


class TeacherWithPracticeResponse(TeacherResponse):
    is_practice: bool


class SubjectWithPracticeResponse(SubjectResponse):
    is_practice: bool


class AdminRegisterRequest(BaseModel):
    username: str
    password: str
