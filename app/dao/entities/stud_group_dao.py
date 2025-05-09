from sqlalchemy.orm import Session
from app.dao.models import StudGroup


class StudGroupDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_all_stud_groups(self):
        return self.db.query(StudGroup).all()

    def create_stud_group(self, group: StudGroup, commit: bool = True):
        self.db.add(group)
        if commit:
            self.db.commit()
            self.db.refresh(group)

    def get_stud_group_by_brs_id(self, brs_id: int):
        return self.db.query(StudGroup).filter(StudGroup.brs_id == brs_id).first()

    def update_group(self, group: StudGroup, commit: bool = True):
        self.db.add(group)
        if commit:
            self.db.commit()
