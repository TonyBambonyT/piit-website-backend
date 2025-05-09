import httpx
from sqlalchemy.orm import Session
from app.dao.entities.subject_dao import SubjectDAO
from app.dao.models import Subject


class SubjectService:
    def __init__(self, db: Session):
        self.dao = SubjectDAO(db)

    def get_all_subjects(self):
        return self.dao.get_all_subjects()

    def create_subjects(self, url: str, commit: bool = True):
        try:
            response = httpx.get(url)
            data = response.json()
            subjects = data.get("subjects", [])
            if subjects:
                self._save_subjects(subjects, commit)
            else:
                raise ValueError("Subjects not found in the response")
        except httpx.RequestError as e:
            raise Exception(f"Error fetching data: {e}")

    def _save_subjects(self, subjects_data: list, commit: bool = True) -> None:
        for subject in subjects_data:
            brs_id = subject.get("id")
            existing_subject = self.dao.get_subject_by_brs_id(brs_id)
            if existing_subject:
                self._update_existing_subject(existing_subject, subject, commit)
            else:
                self._add_new_subject(brs_id, subject, commit)

    def _update_existing_subject(self, existing_subject: Subject, subject: dict, commit: bool = True):
        existing_subject.name = subject.get("name")
        self.dao.update_subject(existing_subject, commit)

    def _add_new_subject(self, brs_id: int, subject: dict, commit: bool = True):
        new_subject = Subject(
            brs_id=brs_id,
            name=subject.get("name")
        )
        self.dao.create_subject(new_subject, commit)

    def get_subjects_by_teacher_id(self, teacher_id: int) -> list[Subject]:
        return self.dao.get_subjects_by_teacher_id(teacher_id)
