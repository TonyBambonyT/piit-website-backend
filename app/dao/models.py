from datetime import datetime
import pytz as pytz
from sqlalchemy import Column, Integer, String, Boolean, ARRAY, DateTime, TEXT, ForeignKey, TIMESTAMP, DATE
from sqlalchemy.orm import relationship
from app.dao.db_config import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, autoincrement=True)
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


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    articles = relationship('Article', back_populates='tag')


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    icon = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(pytz.timezone('Europe/Moscow')))
    title = Column(String, nullable=False)
    views = Column(Integer, default=0)
    content = Column(TEXT, nullable=True)
    event_date = Column(DATE, nullable=False)
    tag_id = Column(Integer, ForeignKey('tags.id'), nullable=False)
    tag = relationship('Tag', back_populates='articles')
