from sqlalchemy.orm import Session
from app.api.dto import ArticleBase
from app.dao.entities.article_dao import ArticleDAO
from app.dao.models import Article


class ArticleService:
    def __init__(self, db: Session):
        self.dao = ArticleDAO(db)

    def get_all_articles(self):
        return self.dao.get_all_articles()

    def create_article(self, article_data: ArticleBase):
        existing_article = self.dao.get_article_by_title(article_data.title)
        if existing_article:
            return None
        new_article = Article(**article_data.dict())
        return self.dao.create_article(new_article)

    def get_latest_articles(self, limit: int = 6):
        return self.dao.get_latest_articles(limit)
