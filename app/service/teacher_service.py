import httpx
from sqlalchemy.orm import Session

from app.api.dto import TeacherBase
from app.dao.entities.teacher_dao import TeacherDAO
from app.dao.models import Teacher


class TeacherService:
    def __init__(self, db: Session):
        self.dao = TeacherDAO(db)

    def get_all_teachers(self):
        return self.dao.get_all_teachers()

    def get_teacher_by_id(self, teacher_id: int):
        return self.dao.get_teacher_by_id(teacher_id)

    def create_teacher(self, teacher: TeacherBase):
        existing_teacher = self.dao.get_teacher_by_person_id(teacher.person_id)
        if existing_teacher:
            return None
        new_teacher = Teacher(**teacher.dict())
        return self.dao.create_teacher(new_teacher)

    def fetch_teachers_from_api(self, url: str):
        """
        Загружает данные учителей из внешнего API.
        """
        try:
            response = httpx.get(url)
            response.raise_for_status()
            data = response.json()

            if not data.get("ok") or "teachers" not in data:
                raise ValueError("Invalid JSON structure")
            return data["teachers"]
        except Exception as e:
            raise RuntimeError(f"Error fetching teachers from API: {e}")

    def synchronize_teachers(self, teachers: list[dict]):
        """
        Синхронизирует базу данных с данными из API.
        """
        for teacher_data in teachers:
            teacher_data.pop("id", None)
            existing_teacher = self.dao.get_teacher_by_person_id(teacher_data["person_id"])
            if existing_teacher:
                self.dao.update_teacher(existing_teacher, teacher_data)
            else:
                new_teacher = Teacher(**teacher_data)
                self.dao.add_teacher(new_teacher)
        self.dao.save_changes()
