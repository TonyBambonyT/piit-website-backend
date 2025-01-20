from sqlalchemy.orm import Session
from src.api.dto import TagBase
from src.dao.entities.tag_dao import TagDAO
from src.dao.models import Tag


class TagService:
    def __init__(self, db: Session):
        self.dao = TagDAO(db)

    def get_all_tags(self):
        return self.dao.get_all_tags()

    def create_tag(self, tag: TagBase):
        existing_tag = self.dao.get_tag_by_name(tag.name)
        if existing_tag:
            return None
        new_tag = Tag(**tag.dict())
        return self.dao.create_tag(new_tag)
