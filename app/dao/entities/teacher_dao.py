from sqlalchemy import case, asc
from sqlalchemy.orm import Session
from app.dao.models import Teacher


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
