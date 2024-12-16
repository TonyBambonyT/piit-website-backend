from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List

from src.api.dto import TeacherBase, TeacherResponse
from src.dao.models import Teachers
from src.dao.session import get_db

router = APIRouter()


@router.get("/", response_model=List[TeacherResponse])
def get_all_teachers(db: Session = Depends(get_db)):
    teachers = db.query(Teachers).all()
    if not teachers:
        raise HTTPException(status_code=404, detail="No teachers found")
    return teachers


@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher_by_id(
    teacher_id: int = Path(..., title="ID учителя", description="Уникальный идентификатор учителя"),
    db: Session = Depends(get_db),
):
    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail=f"Teacher with ID {teacher_id} not found")
    return teacher


@router.post("/", response_model=TeacherResponse)
def create_teacher(teacher: TeacherBase, db: Session = Depends(get_db)):
    existing_teacher = db.query(Teachers).filter(Teachers.person_id == teacher.person_id).first()
    if existing_teacher:
        raise HTTPException(status_code=400, detail="Teacher with this person_id already exists")

    new_teacher = Teachers(**teacher.dict())
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher
