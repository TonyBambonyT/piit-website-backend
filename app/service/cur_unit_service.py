from app.dao.entities.cur_unit_dao import CurriculumUnitDAO
from app.dao.models import CurriculumUnit
from app.service.common.utils import fetch_data_until_found


class CurriculumUnitService:
    def __init__(self, db):
        self.dao = CurriculumUnitDAO(db)

    def get_all_curriculum_units(self):
        return self.dao.get_all_curriculum_units()

    def get_curriculum_unit_by_brs_id(self, brs_id):
        return self.dao.get_cur_unit_by_brs_id(brs_id)

    def create_curriculum_units(self, url_template, commit: bool = True):
        fetch_data_until_found(
            url_template,
            extract_fn=lambda data: data.get("curriculum_units", []),
            save_fn=lambda units: self._save_curriculum_unit(units, commit=commit)
        )

    def _save_curriculum_unit(self, units: list, commit: bool = True):
        for unit in units:
            brs_id = unit.get("id")
            existing = self.dao.get_cur_unit_by_brs_id(brs_id)
            if existing:
                self._update_existing_unit(existing, unit, commit)
            else:
                self._add_new_unit(brs_id, unit, commit)

    def _update_existing_unit(self, existing_unit: CurriculumUnit, data: dict, commit: bool = True):
        existing_unit.practice_teacher_brs_ids = data.get("practice_teacher_ids", [])
        existing_unit.stud_group_brs_id = data["stud_group_id"]
        existing_unit.subject_brs_id = data["subject_id"]
        existing_unit.teacher_brs_id = data["teacher_id"]
        self.dao.update_curriculum_unit(existing_unit, commit)

    def _add_new_unit(self, brs_id: int, data: dict, commit: bool = True):
        unit = CurriculumUnit(
            brs_id=brs_id,
            practice_teacher_brs_ids=data.get("practice_teacher_ids", []),
            stud_group_brs_id=data["stud_group_id"],
            subject_brs_id=data["subject_id"],
            teacher_brs_id=data["teacher_id"]
        )
        self.dao.create_curriculum_unit(unit, commit)

    def get_full_curriculum_unit_info_by_id(self, id_: int):
        return self.dao.get_cur_unit_full_info_by_id(id_)

    def get_full_curriculum_unit_info_by_brs_id(self, brs_id: int):
        return self.dao.get_cur_unit_full_info_by_brs_id(brs_id)

    def get_all_full_curriculum_units(self):
        return self.dao.get_all_cur_units_full_info()
