from sqlalchemy.orm import Session
from app.config.config import settings
from app.dao.models import TeacherCurriculumUnitLink, StudGroup, Subject, Teacher, CurriculumUnit
from app.service.cur_unit_service import CurriculumUnitService
from app.service.stud_group_service import StudGroupService
from app.service.subject_service import SubjectService
from app.service.teacher_service import TeacherService


class DataSyncManager:
    def __init__(self, db: Session):
        self.db = db
        self.teacher_service = TeacherService(db)
        self.subject_service = SubjectService(db)
        self.stud_group_service = StudGroupService(db)
        self.curriculum_unit_service = CurriculumUnitService(db)

    def sync_all(self):
        with self.db.begin():  # атомарная транзакция
            self._truncate_all()
            self._sync_all()
            self.db.flush()
            self._rebuild_links()

    def _truncate_all(self):
        self.db.query(TeacherCurriculumUnitLink).delete()
        self.db.query(CurriculumUnit).delete()
        self.db.query(StudGroup).delete()
        self.db.query(Subject).delete()
        self.db.query(Teacher).delete()

    def _sync_all(self):
        teachers = self.teacher_service.fetch_teachers_from_api(settings.TEACHERS_URI)
        self.teacher_service.synchronize_teachers(teachers, commit=False)
        self.subject_service.create_subjects(settings.SUBJECTS_URI, commit=False)
        self.stud_group_service.create_stud_groups(settings.STUB_GROUPS_URI, commit=False)
        self.curriculum_unit_service.create_curriculum_units(settings.CUR_UNITS_URI, commit=False)

    def _rebuild_links(self):
        self.db.query(TeacherCurriculumUnitLink).delete()
        teachers_by_brs_id = {
            t.brs_id: t.id
            for t in self.db.query(Teacher.id, Teacher.brs_id).all()
        }
        curriculum_units = self.db.query(CurriculumUnit).all()
        links = []
        for unit in curriculum_units:
            main_id = teachers_by_brs_id.get(unit.teacher_brs_id)
            if main_id:
                links.append(TeacherCurriculumUnitLink(
                    teacher_id=main_id,
                    curriculum_unit_id=unit.id,
                    is_practice=False
                ))
            for brs_id in unit.practice_teacher_brs_ids:
                practice_id = teachers_by_brs_id.get(brs_id)
                if practice_id:
                    links.append(TeacherCurriculumUnitLink(
                        teacher_id=practice_id,
                        curriculum_unit_id=unit.id,
                        is_practice=True
                    ))
        self.db.bulk_save_objects(links)
