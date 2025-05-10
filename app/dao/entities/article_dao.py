from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case, extract, distinct
from app.dao.models import Article, Tag, ArticleTagAssociation


class ArticleDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_all_articles(self):
        return self.db.query(Article).all()

    def get_tags_by_ids(self, tag_ids: list[int]):
        return self.db.query(Tag).filter(Tag.id.in_(tag_ids)).all()

    def get_article_by_title(self, title: str):
        return self.db.query(Article).filter(Article.title == title).first()

    def get_article_by_id(self, article_id: int):
        return self.db.query(Article).filter(Article.id == article_id).first()

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
        query = self.db.query(Article)
        if tags:
            tag_count = len(tags)
            query = (
                query.join(ArticleTagAssociation)
                .join(Tag)
                .filter(Tag.name.in_(tags))
                .group_by(Article.id)
                .having(func.count(distinct(Tag.name)) == tag_count)
            )
        if year_min is not None:
            query = query.filter(extract("year", Article.event_date) >= year_min)
        if year_max is not None:
            query = query.filter(extract("year", Article.event_date) <= year_max)
        if month_min is not None:
            query = query.filter(extract("month", Article.event_date) >= month_min)
        if month_max is not None:
            query = query.filter(extract("month", Article.event_date) <= month_max)
        query = query.options(joinedload(Article.tags))
        query = query.order_by(Article.event_date.desc()) \
            .offset((page - 1) * limit) \
            .limit(limit)

        return query.all()

    def update_article(self, article: Article):
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

    def delete_article(self, article: Article):
        self.db.delete(article)
        self.db.commit()
