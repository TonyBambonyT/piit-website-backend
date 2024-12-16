from pydantic import BaseModel
from typing import List


class TeacherBase(BaseModel):
    """
    Базовая DTO-шка для модели Teachers.
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
