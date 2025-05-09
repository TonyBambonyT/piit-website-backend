from sqlalchemy.orm import Session, aliased
from app.api.dto import SubjectWithPracticeResponse
from app.dao.models import Subject, TeacherCurriculumUnitLink, CurriculumUnit


class SubjectDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_all_subjects(self):
        return self.db.query(Subject).all()

    def create_subject(self, subject: Subject, commit: bool = True):
        self.db.add(subject)
        if commit:
            self.db.commit()
            self.db.refresh(subject)

    def get_subject_by_brs_id(self, brs_id: int):
        return self.db.query(Subject).filter(Subject.brs_id == brs_id).first()

    def update_subject(self, subject: Subject, commit: bool = True):
        self.db.add(subject)
        if commit:
            self.db.commit()

    def get_subjects_by_teacher_id(self, teacher_id: int) -> list[SubjectWithPracticeResponse]:
        link_alias = aliased(TeacherCurriculumUnitLink)

        results = (
            self.db.query(Subject, link_alias.is_practice)
            .join(CurriculumUnit, CurriculumUnit.subject_brs_id == Subject.brs_id)
            .join(link_alias, link_alias.curriculum_unit_id == CurriculumUnit.id)
            .filter(link_alias.teacher_id == teacher_id)
            .distinct()
            .all()
        )

        return [
            SubjectWithPracticeResponse(
                **subject.__dict__,
                is_practice=is_practice
            )
            for subject, is_practice in results
        ]
