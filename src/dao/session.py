from sqlalchemy.orm import Session
from src.dao.db_config import SessionLocal


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
