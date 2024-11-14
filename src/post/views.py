from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List


from .schemas import PostCreate, Post as PostSchema, ShowPost
from .service import (
    create_post_svc,
    create_hashtags_svc,
    get_user_post_svc,
    get_hashtag_posts_svc,
    get_random_posts_svc,
    get_post_from_id_svc,
    delete_post_svc,
    like_post_svc,
    unlike_post_svc,
    liked_users_post_svc,
)
from ..auth.service import (
    get_current_user,
    get_current_user_from_user_id,
    existing_user,
)

router = APIRouter(prefix="/posts", tags=["posts"])


# create posts by a user
@router.post("/", response_model=PostSchema, status_code=status.HTTP_201_CREATED)
async def create_post(request: PostCreate, token: str, db: Session = Depends(get_db)):
    # verify the token  to be sure
    user = await get_current_user(db, token)
    if not user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized to perform function",
        )
    # create posts now
    post = await create_post_svc(request, db, user.id)
    return post


# get posts of current user
@router.get("/", response_model=List[ShowPost], status_code=status.HTTP_200_OK)
async def get_current_posts_from_user(token: str, db: Session = Depends(get_db)):
    user = await get_current_user(db, token)
    if not user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not exist",
        )
    return await get_user_post_svc(user.id, db)


# get posts of any users N.B!! with their username
@router.get(
    "/user/{username}", response_model=List[ShowPost], status_code=status.HTTP_200_OK
)
async def get_user_post(username: str, db: Session = Depends(get_db)):
    user = await existing_user(db, username=username)
    # user id
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )
    posts = await get_post_from_id_svc(db, user.id)
    return posts


@router.get("/hashtag/{hashtag}")
async def get_posts_from_hashtags(hashtag: str, db: Session = Depends(get_db)):
    return await get_hashtag_posts_svc(hashtag, db)


@router.get("/feed/posts")
async def get_random_posts(
    page: int = 1, limit: int = 5, hashtag: str = None, db: Session = Depends(get_db)
):
    return await get_random_posts_svc(db, page, limit, hashtag)
