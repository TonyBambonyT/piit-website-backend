from fastapi import Depends
from sqlalchemy.orm import Session

from src.dao.session import get_db
from src.service.article_service import ArticleService
from src.service.tag_service import TagService
from src.service.teacher_service import TeacherService


def get_teacher_service(db: Session = Depends(get_db)) -> TeacherService:
    return TeacherService(db)


def get_tag_service(db: Session = Depends(get_db)) -> TagService:
    return TagService(db)


def get_article_service(db: Session = Depends(get_db)) -> ArticleService:
    return ArticleService(db)
