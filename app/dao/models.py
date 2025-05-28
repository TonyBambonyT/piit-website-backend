from datetime import datetime
import pytz as pytz
from sqlalchemy import Column, Integer, String, Boolean, ARRAY, TEXT, ForeignKey, TIMESTAMP, DATE
from sqlalchemy.orm import relationship
from app.dao.db_config import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    icon = Column(String, nullable=True)
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
    brs_id = Column(Integer, nullable=False, unique=True)
    curriculum_units = relationship("CurriculumUnit", back_populates="teacher")
    linked_units = relationship("TeacherCurriculumUnitLink", back_populates="teacher", cascade="all, delete")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    article_associations = relationship(
        "ArticleTagAssociation", back_populates="tag", cascade="all, delete-orphan"
    )
    articles = relationship(
        "Article", secondary="article_tag_association", back_populates="tags"
    )


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    icon = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        default=lambda: datetime.now(pytz.timezone('Europe/Moscow')))
    title = Column(String, nullable=False)
    views = Column(Integer, default=0)
    content = Column(TEXT, nullable=True)
    event_date = Column(DATE, nullable=False)
    tag_associations = relationship(
        "ArticleTagAssociation", back_populates="article", cascade="all, delete-orphan"
    )
    tags = relationship(
        "Tag", secondary="article_tag_association", back_populates="articles"
    )


class ArticleTagAssociation(Base):
    __tablename__ = "article_tag_association"
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    tag_id = Column(Integer, ForeignKey("tags.id"))

    article = relationship("Article", back_populates="tag_associations")
    tag = relationship("Tag", back_populates="article_associations")


class CurriculumUnit(Base):
    __tablename__ = "curriculum_units"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brs_id = Column(Integer, nullable=False, unique=True)
    practice_teacher_brs_ids = Column(ARRAY(Integer), nullable=False, default=[])
    stud_group_brs_id = Column(Integer, ForeignKey('stud_groups.brs_id'), nullable=False)
    teacher_brs_id = Column(Integer, ForeignKey('teachers.brs_id'), nullable=False)
    subject_brs_id = Column(Integer, ForeignKey('subjects.brs_id'), nullable=False)
    teacher = relationship("Teacher", back_populates="curriculum_units", primaryjoin="CurriculumUnit.teacher_brs_id==Teacher.brs_id")
    subject = relationship("Subject", back_populates="curriculum_units", primaryjoin="CurriculumUnit.subject_brs_id==Subject.brs_id")
    stud_group = relationship("StudGroup", back_populates="curriculum_units", primaryjoin="CurriculumUnit.stud_group_brs_id==StudGroup.brs_id")
    linked_teachers = relationship("TeacherCurriculumUnitLink", back_populates="curriculum_unit", cascade="all, delete")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brs_id = Column(Integer, nullable=False, unique=True)
    name = Column(String, nullable=False)
    curriculum_units = relationship("CurriculumUnit", back_populates="subject")


class StudGroup(Base):
    __tablename__ = "stud_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brs_id = Column(Integer, nullable=False, unique=True)
    course = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    education_level = Column(String, nullable=False)
    curriculum_units = relationship("CurriculumUnit", back_populates="stud_group")


class TeacherCurriculumUnitLink(Base):
    __tablename__ = "teacher_curriculum_unit_link"
    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    curriculum_unit_id = Column(Integer, ForeignKey("curriculum_units.id", ondelete="CASCADE"), nullable=False)
    is_practice = Column(Boolean, default=False)
    teacher = relationship("Teacher", back_populates="linked_units")
    curriculum_unit = relationship("CurriculumUnit", back_populates="linked_teachers")


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
