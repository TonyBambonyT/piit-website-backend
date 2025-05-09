from fastapi import Depends
from sqlalchemy.orm import Session

from app.dao.session import get_db
from app.service.article_service import ArticleService
from app.service.auth_service import AdminUserService
from app.service.common.data_sync_manager import DataSyncManager
from app.service.cur_unit_service import CurriculumUnitService
from app.service.stud_group_service import StudGroupService
from app.service.subject_service import SubjectService
from app.service.tag_service import TagService
from app.service.teacher_service import TeacherService


def get_teacher_service(db: Session = Depends(get_db)) -> TeacherService:
    return TeacherService(db)


def get_tag_service(db: Session = Depends(get_db)) -> TagService:
    return TagService(db)


def get_article_service(db: Session = Depends(get_db)) -> ArticleService:
    return ArticleService(db)


def get_curriculum_unit_service(db: Session = Depends(get_db)) -> CurriculumUnitService:
    return CurriculumUnitService(db)


def get_subject_service(db: Session = Depends(get_db)) -> SubjectService:
    return SubjectService(db)


def get_stud_group_service(db: Session = Depends(get_db)) -> StudGroupService:
    return StudGroupService(db)


def get_data_sync_manager(db: Session = Depends(get_db)) -> DataSyncManager:
    return DataSyncManager(db)


def get_admin_user_service(db: Session = Depends(get_db)) -> AdminUserService:
    return AdminUserService(db)
