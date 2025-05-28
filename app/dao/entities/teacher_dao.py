from sqlalchemy import case, asc
from sqlalchemy.orm import Session, aliased
from app.api.dto import TeacherWithPracticeResponse
from app.dao.models import Teacher, Subject, CurriculumUnit, TeacherCurriculumUnitLink


class TeacherDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_all_teachers(self):
        return self.db.query(Teacher).filter(Teacher.rank_short != "магистр").order_by(
            case(
                (Teacher.surname == "Махортов", 0),
                else_=1
            ),
            asc(Teacher.surname)
        ).all()

    def get_teacher_by_id(self, teacher_id: int):
        return self.db.query(Teacher).filter(Teacher.id == teacher_id).first()

    def get_teacher_by_person_id(self, person_id: int):
        return self.db.query(Teacher).filter(Teacher.person_id == person_id).first()

    def create_teacher(self, teacher: Teacher):
        self.db.add(teacher)
        self.db.commit()
        self.db.refresh(teacher)
        return teacher

    def update_teacher(self, teacher: Teacher, data: dict):
        for key, value in data.items():
            if key == "id":  # Игнорируем id
                continue
            setattr(teacher, key, value)

    def add_teacher(self, teacher: Teacher):
        self.db.add(teacher)

    def save_changes(self):
        self.db.commit()

    def get_cur_unit_full_info_by_id(self, id_: int):
        unit = (
            self.db.query(CurriculumUnit)
            .filter(CurriculumUnit.id == id_)
            .join(CurriculumUnit.teacher)
            .join(CurriculumUnit.subject)
            .join(CurriculumUnit.stud_group)
            .first()
        )

        if not unit:
            return None

        teacher_brs_id_map = {t.brs_id: t for t in self.db.query(Teacher).all()}
        unit.practice_teachers = [
            teacher_brs_id_map[tid]
            for tid in unit.practice_teacher_brs_ids
            if tid in teacher_brs_id_map
        ]
        return unit

    def get_teachers_by_subject_id(self, subject_id: int) -> list[TeacherWithPracticeResponse]:
        link_alias = aliased(TeacherCurriculumUnitLink)

        results = (
            self.db.query(Teacher, link_alias.is_practice)
            .join(link_alias, link_alias.teacher_id == Teacher.id)
            .join(CurriculumUnit, CurriculumUnit.id == link_alias.curriculum_unit_id)
            .join(Subject, Subject.brs_id == CurriculumUnit.subject_brs_id)
            .filter(Subject.id == subject_id)
            .distinct()
            .all()
        )

        return [
            TeacherWithPracticeResponse(
                **teacher.__dict__,
                is_practice=is_practice
            )
            for teacher, is_practice in results
        ]

    def update_teacher_icon(self, teacher_id: int, icon_path: str) -> None:
        teacher = self.db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if teacher:
            teacher.icon = icon_path
            self.db.commit()
