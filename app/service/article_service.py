from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.api.dto import ArticleBase, ArticleResponse
from app.dao.entities.article_dao import ArticleDAO
from app.dao.models import Article, ArticleTagAssociation
from app.service.common.utils import save_icon_file


class ArticleService:
    def __init__(self, db: Session):
        self.dao = ArticleDAO(db)

    def create_article(self, article_data: ArticleBase):
        existing_article = self.dao.get_article_by_title(article_data.title)
        if existing_article:
            return None
        tags = self.dao.get_tags_by_ids(article_data.tag_ids)
        associations = [ArticleTagAssociation(tag=tag) for tag in tags]
        article_dict = article_data.dict()
        del article_dict["tag_ids"]
        new_article = Article(**article_dict, tag_associations=associations)
        saved_article = self.dao.create_article(new_article)
        return self.to_response_dto(saved_article)

    def get_latest_articles(self, limit: int = 6):
        articles = self.dao.get_latest_articles(limit)
        return [self.to_response_dto(a) for a in articles]

    def get_article_by_id(self, article_id: int):
        article = self.dao.get_article_by_id(article_id)
        if not article:
            return None
        return self.to_response_dto(article)

    def get_filtered_articles(
            self,
            year_min: int | None,
            year_max: int | None,
            month_min: int | None,
            month_max: int | None,
            tags: list[str] | None,
            page: int,
            limit: int
    ):
        articles = self.dao.get_filtered_articles(year_min, year_max, month_min, month_max, tags, page, limit)
        return [self.to_response_dto(a) for a in articles]

    def update_article_with_optional_fields(
            self,
            article_id: int,
            icon: UploadFile = None,
            title: str = None,
            content: str = None,
            tag_ids: list[int] = None,
            event_date: str = None,
    ) -> ArticleResponse | None:
        article = self.dao.get_article_by_id(article_id)
        if not article:
            return None
        if icon and icon.filename:
            article.icon = save_icon_file(icon, prefix=title or article.title)
        if title not in (None, "", "null"):
            article.title = title
        if content not in (None, "", "null"):
            article.content = content
        if tag_ids is not None:
            tags = self.dao.get_tags_by_ids(tag_ids)
            article.tag_associations = [ArticleTagAssociation(tag=tag) for tag in tags]
        if event_date not in (None, "", "null"):
            article.event_date = datetime.fromisoformat(event_date).date()
        updated_article = self.dao.update_article(article)
        return self.to_response_dto(updated_article)

    def delete_article(self, article_id: int):
        article = self.dao.get_article_by_id(article_id)
        if not article:
            return False
        self.dao.delete_article(article)
        return True

    @staticmethod
    def to_response_dto(article: Article) -> ArticleResponse:
        return ArticleResponse(
            id=article.id,
            icon=article.icon,
            title=article.title,
            content=article.content,
            tag_ids=[tag.id for tag in article.tags],
            event_date=article.event_date,
            created_at=article.created_at,
            views=article.views,
        )
