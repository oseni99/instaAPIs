# db models
from datetime import date, datetime, timezone

from sqlalchemy import (
    DATETIME,
    Boolean,
    Column,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship, validates

from ..database import Base
from ..post.models import post_likes
from .enums import Gender


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created_date = Column(DATETIME, default=datetime.now(timezone.utc))

    # profile related

    dob = Column(Date)
    gender = Column(Enum(Gender))
    profile_pic = Column(String)
    bio = Column(String)
    location = Column(String)
    posts = relationship("Post", back_populates="author")

    liked_post = relationship("Post", secondary=post_likes, back_populates="user_liked")

    @validates("dob")
    def validate_dob(self, key, dob):
        if dob >= date.today():
            raise ValueError("Date of birth must be in the past")
        return dob
