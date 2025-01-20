from datetime import datetime
import pytz as pytz
from sqlalchemy import Column, Integer, String, Boolean, ARRAY, DateTime, TEXT, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from src.dao.db_config import Base


class Teacher(Base):
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


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)  # Уникальный идентификатор тега
    name = Column(String, nullable=False)  # Название тега
    articles = relationship('Article', back_populates='tag')  # Связь со статьями (один ко многим)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)  # Уникальный идентификатор статьи
    icon = Column(String, nullable=True)  # Иконка статьи
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(pytz.timezone('Europe/Moscow')))  # Дата и время создания статьи
    title = Column(String, nullable=False)  # Заголовок статьи
    views = Column(Integer, default=0)  # Количество просмотров статьи
    content = Column(TEXT, nullable=True)  # Содержание статьи (вложенный JSON)
    tag_id = Column(Integer, ForeignKey('tags.id'), nullable=False)  # Внешний ключ на таблицу тегов
    tag = relationship('Tag', back_populates='articles')  # Связь с тегом (один к одному с точки зрения статьи)
