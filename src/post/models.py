from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import relationship

from ..database import Base

# Association Table for a many to many relationship with SQLalchemy
post_hashtags = Table(
    "post_hashtags", # name
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id")),
    Column("hashtags_id", Integer, ForeignKey("hashtags.id")),
)

post_likes = Table(
    "post_likes", # table name
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("post_id", Integer, ForeignKey("posts.id")),
)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    image = Column(String)  # url of the image
    location = Column(String)
    created_dt = Column(DateTime, default=datetime.now(timezone.utc))
    likes_count = Column(Integer, default=0)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")

    hashtags = relationship("Hashtag", secondary=post_hashtags, back_populates="posts")

    user_liked = relationship("User", secondary=post_likes, back_populates="liked_post")


class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    posts = relationship("Post", secondary=post_hashtags, back_populates="hashtags")
