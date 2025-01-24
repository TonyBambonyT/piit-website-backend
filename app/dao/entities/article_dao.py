from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.dao.models import Article


class ArticleDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_all_articles(self):
        return self.db.query(Article).all()

    def get_article_by_title(self, title: str):
        return self.db.query(Article).filter(Article.title == title).first()

    def create_article(self, article: Article):
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

    def get_latest_articles(self, limit: int = 6):
        today = (datetime.utcnow() + timedelta(hours=3)).date()
        days_diff = func.abs(func.date(Article.event_date) - today)
        case_order = case(
            {
                True: 0,
                False: 1
            },
            value=(Article.event_date >= today)
        )
        return (self.db.query(Article)
                .order_by(days_diff, case_order, Article.event_date)
                .limit(limit)
                .all())
