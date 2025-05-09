from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.api.dto import ArticleBase
from app.dao.entities.article_dao import ArticleDAO
from app.dao.models import Article
from app.service.common.utils import save_icon_file


class ArticleService:
    def __init__(self, db: Session):
        self.dao = ArticleDAO(db)

    def create_article(self, article_data: ArticleBase):
        existing_article = self.dao.get_article_by_title(article_data.title)
        if existing_article:
            return None
        new_article = Article(**article_data.dict())
        return self.dao.create_article(new_article)

    def get_latest_articles(self, limit: int = 6):
        return self.dao.get_latest_articles(limit)

    def get_article_by_id(self, article_id: int):
        return self.dao.get_article_by_id(article_id)

    def get_filtered_articles(
            self, year: int | None,
            month: int | None,
            tags: list[str] | None,
            page: int,
            limit: int
    ):
        return self.dao.get_filtered_articles(year, month, tags, page, limit)

    def update_article_with_optional_fields(
            self,
            article_id: int,
            icon: UploadFile = None,
            title: str = None,
            content: str = None,
            tag_id: int = None,
            event_date: datetime.date = None,
    ):
        article = self.dao.get_article_by_id(article_id)
        if not article:
            return None
        if icon and icon.filename:
            article.icon = save_icon_file(icon, prefix=title or article.title)
        if title not in (None, "", "null"):
            article.title = title
        if content not in (None, "", "null"):
            article.content = content
        if tag_id not in (None, "", "null"):
            article.tag_id = int(tag_id)
        if event_date not in (None, "", "null"):
            article.event_date = datetime.fromisoformat(event_date).date()
        return self.dao.update_article(article)

    def delete_article(self, article_id: int):
        article = self.dao.get_article_by_id(article_id)
        if not article:
            return False
        self.dao.delete_article(article)
        return True
