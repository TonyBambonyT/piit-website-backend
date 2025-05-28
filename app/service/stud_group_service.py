from app.dao.entities.stud_group_dao import StudGroupDAO
from app.dao.models import StudGroup
from app.service.common.utils import fetch_data_until_found, collect_data_until_found


class StudGroupService:
    def __init__(self, db):
        self.dao = StudGroupDAO(db)

    def get_all_stud_groups(self):
        return self.dao.get_all_stud_groups()

    @staticmethod
    def fetch_groups(url_template: str) -> list[dict]:
        return collect_data_until_found(url_template, lambda d: d.get("stud_groups", []))

    def create_stud_groups(self, url_template, commit: bool = True):
        fetch_data_until_found(
            url_template,
            extract_fn=lambda data: data.get("stud_groups", []),
            save_fn=lambda groups: self._save_group(groups, commit=commit)
        )

    def _save_group(self, group_data: list, commit: bool = True) -> None:
        for group in group_data:
            brs_id = group.get("id")
            existing_group = self.dao.get_stud_group_by_brs_id(brs_id)
            if existing_group:
                self._update_existing_group(existing_group, group, commit)
            else:
                self._add_new_group(brs_id, group, commit)

    def _update_existing_group(self, existing_group: StudGroup, group: dict, commit: bool = True):
        existing_group.course = group.get("course")
        existing_group.semester = group.get("semester")
        existing_group.education_level = group.get("education_level")
        self.dao.update_group(existing_group, commit)

    def _add_new_group(self, brs_id: int, group: dict, commit: bool = True):
        new_group = StudGroup(
            brs_id=brs_id,
            course=group.get("course"),
            semester=group.get("semester"),
            education_level=group.get("education_level")
        )
        self.dao.create_stud_group(new_group, commit)
