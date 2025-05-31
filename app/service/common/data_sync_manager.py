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
        with self.db.begin():
            teachers = self.teacher_service.fetch_teachers_from_api(settings.TEACHERS_URI)
            subjects = self.subject_service.fetch_subjects(settings.SUBJECTS_URI)
            groups = self.stud_group_service.fetch_groups(settings.STUB_GROUPS_URI)
            units = self.curriculum_unit_service.fetch_units(settings.CUR_UNITS_URI)
            self._clean_links(teachers, units)
            self._sync_entities(Teacher, teachers, 'brs_id')
            self._sync_entities(Subject, subjects, 'brs_id')
            self._sync_entities(StudGroup, groups, 'brs_id')
            self._sync_entities(CurriculumUnit, units, 'brs_id')
            self.db.flush()
            self._rebuild_links()

    def _clean_links(self, teachers: list[dict], units: list[dict]):
        teacher_brs_ids = {t["id"] for t in teachers}
        unit_brs_ids = {u["id"] for u in units}
        teacher_ids = [t.id for t in self.db.query(Teacher).filter(~Teacher.brs_id.in_(teacher_brs_ids))]
        unit_ids = [u.id for u in self.db.query(CurriculumUnit).filter(~CurriculumUnit.brs_id.in_(unit_brs_ids))]
        if teacher_ids:
            self.db.query(TeacherCurriculumUnitLink).filter(
                TeacherCurriculumUnitLink.teacher_id.in_(teacher_ids)
            ).delete(synchronize_session=False)
        if unit_ids:
            self.db.query(TeacherCurriculumUnitLink).filter(
                TeacherCurriculumUnitLink.curriculum_unit_id.in_(unit_ids)
            ).delete(synchronize_session=False)

    def _sync_entities(self, model, new_data: list[dict], brs_field: str):
        existing = {
            getattr(obj, brs_field): obj
            for obj in self.db.query(model).all()
        }
        new_ids = set()

        FIELD_RENAMES = {
            CurriculumUnit: {
                "practice_teacher_ids": "practice_teacher_brs_ids",
                "stud_group_id": "stud_group_brs_id",
                "subject_id": "subject_brs_id",
                "teacher_id": "teacher_brs_id",
            }
        }
        model_columns = {col.name for col in model.__table__.columns}

        for item in new_data:
            brs_id = item.get("id")
            new_ids.add(brs_id)
            obj = existing.get(brs_id)
            item["brs_id"] = item.pop("id")

            for old_key, new_key in FIELD_RENAMES.get(model, {}).items():
                if old_key in item:
                    item[new_key] = item.pop(old_key)
            item = {key: value for key, value in item.items() if key in model_columns}
            if obj:
                for key, value in item.items():
                    if model is Teacher and key == "icon":
                        continue  # иконку преподавателя не трогаем
                    setattr(obj, key, value)
            else:
                # Логика только для новых учителей
                if model is Teacher:
                    gender = item.get("gender")
                    if "icon" not in item or item["icon"] is None:
                        if gender == "M":
                            item["icon"] = settings.DEFAULT_MAN_ICON
                        elif gender == "W":
                            item["icon"] = settings.DEFAULT_WOMAN_ICON

                self.db.add(model(**item))

        to_delete = [obj for brs, obj in existing.items() if brs not in new_ids]
        for obj in to_delete:
            self.db.delete(obj)

    def _rebuild_links(self):
        teachers_by_brs_id = {
            t.brs_id: t.id
            for t in self.db.query(Teacher.id, Teacher.brs_id).all()
        }
        existing_links = {
            (link.teacher_id, link.curriculum_unit_id, link.is_practice)
            for link in self.db.query(
                TeacherCurriculumUnitLink.teacher_id,
                TeacherCurriculumUnitLink.curriculum_unit_id,
                TeacherCurriculumUnitLink.is_practice
            ).all()
        }
        curriculum_units = self.db.query(CurriculumUnit).all()
        new_links = []
        for unit in curriculum_units:
            main_id = teachers_by_brs_id.get(unit.teacher_brs_id)
            if main_id:
                key = (main_id, unit.id, False)
                if key not in existing_links:
                    new_links.append(TeacherCurriculumUnitLink(
                        teacher_id=main_id,
                        curriculum_unit_id=unit.id,
                        is_practice=False
                    ))
            for brs_id in unit.practice_teacher_brs_ids or []:
                practice_id = teachers_by_brs_id.get(brs_id)
                if practice_id:
                    key = (practice_id, unit.id, True)
                    if key not in existing_links:
                        new_links.append(TeacherCurriculumUnitLink(
                            teacher_id=practice_id,
                            curriculum_unit_id=unit.id,
                            is_practice=True
                        ))
        self.db.bulk_save_objects(new_links)
