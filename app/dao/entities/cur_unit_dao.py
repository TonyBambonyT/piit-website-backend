from typing import Type
from sqlalchemy.orm import Session
from app.dao.models import CurriculumUnit, Teacher, Subject, StudGroup


class CurriculumUnitDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_all_curriculum_units(self) -> list[Type[CurriculumUnit]]:
        return self.db.query(CurriculumUnit).all()

    def create_curriculum_unit(self, unit: CurriculumUnit, commit: bool = True):
        self.db.add(unit)
        if commit:
            self.db.commit()
            self.db.refresh(unit)

    def get_cur_unit_by_brs_id(self, brs_id: int):
        return self.db.query(CurriculumUnit).filter(CurriculumUnit.brs_id == brs_id).first()

    def update_curriculum_unit(self, unit: CurriculumUnit, commit: bool = True):
        self.db.add(unit)
        if commit:
            self.db.commit()

    def get_cur_unit_full_info_by_id(self, id_: int):
        unit = self.db.query(CurriculumUnit).filter(CurriculumUnit.id == id_).first()
        return self._enrich_unit(unit)

    def get_cur_unit_full_info_by_brs_id(self, brs_id: int):
        unit = self.db.query(CurriculumUnit).filter(CurriculumUnit.brs_id == brs_id).first()
        return self._enrich_unit(unit)

    def _enrich_unit(self, unit: CurriculumUnit | None) -> CurriculumUnit | None:
        if not unit:
            return None

        unit.teacher = self.db.query(Teacher).filter(Teacher.brs_id == unit.teacher_brs_id).first()
        unit.subject = self.db.query(Subject).filter(Subject.brs_id == unit.subject_brs_id).first()
        unit.stud_group = self.db.query(StudGroup).filter(StudGroup.brs_id == unit.stud_group_brs_id).first()
        unit.practice_teachers = (
            self.db.query(Teacher)
            .filter(Teacher.brs_id.in_(unit.practice_teacher_brs_ids))
            .all()
            if unit.practice_teacher_brs_ids else []
        )
        return unit

    def get_all_cur_units_full_info(self):
        units = self.db.query(CurriculumUnit).all()
        teacher_map = {t.brs_id: t for t in self.db.query(Teacher).all()}
        subject_map = {s.brs_id: s for s in self.db.query(Subject).all()}
        group_map = {g.brs_id: g for g in self.db.query(StudGroup).all()}

        for unit in units:
            unit.teacher = teacher_map.get(unit.teacher_brs_id)
            unit.subject = subject_map.get(unit.subject_brs_id)
            unit.stud_group = group_map.get(unit.stud_group_brs_id)
            unit.practice_teachers = [
                teacher_map[tid]
                for tid in unit.practice_teacher_brs_ids
                if tid in teacher_map
            ]
        return units
