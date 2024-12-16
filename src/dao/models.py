from sqlalchemy import Column, Integer, String, Boolean, ARRAY
from src.dao.db_config import Base


class Teachers(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    academic_degree = Column(String, nullable=True)
    department_id = Column(Integer, nullable=False)
    department_leader = Column(Boolean, default=False)
    department_part_time_job_ids = Column(ARRAY(Integer), default=[])
    department_secretary = Column(Boolean, default=False)
    firstname = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    middlename = Column(String, nullable=True)
    person_id = Column(Integer, nullable=False)
    rank = Column(String, nullable=False)
    rank_short = Column(String, nullable=True)
    surname = Column(String, nullable=False)
