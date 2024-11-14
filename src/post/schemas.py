from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class PostCreate(BaseModel):
    content: Optional[str] = None
    image: str
    location: Optional[str] = None

    class Config:
        from_attributes = True


class Post(PostCreate):
    id: int
    created_dt: datetime
    likes_count: int
    author_id: int

    class Config:
        from_attributes = True


class Hashtag(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ShowPost(BaseModel):
    content: str
    image: str
    location: str
    created_dt: datetime
    likes_count: int
    author: str
    hashtags: Optional[List[str]] = []  # Assuming hashtags are a list
    user_liked: Optional[List[str]] = []

    class Config:
        from_attributes = True
