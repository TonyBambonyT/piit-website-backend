from sqlalchemy.orm import Session
from app.dao.models import Tag


class TagDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_all_tags(self):
        return self.db.query(Tag).all()

    def get_tag_by_name(self, name: str):
        return self.db.query(Tag).filter(Tag.name == name).first()

    def create_tag(self, tag: Tag):
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag
