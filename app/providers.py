from fastapi import Depends
from sqlalchemy.orm import Session

from app.dao.session import get_db
from app.service.article_service import ArticleService
from app.service.tag_service import TagService
from app.service.teacher_service import TeacherService


def get_teacher_service(db: Session = Depends(get_db)) -> TeacherService:
    return TeacherService(db)


def get_tag_service(db: Session = Depends(get_db)) -> TagService:
    return TagService(db)


def get_article_service(db: Session = Depends(get_db)) -> ArticleService:
    return ArticleService(db)
