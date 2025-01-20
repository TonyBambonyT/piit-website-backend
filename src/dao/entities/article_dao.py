from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.dao.models import Article


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
        return self.db.query(Article).order_by(desc(Article.created_at)).limit(limit).all()
