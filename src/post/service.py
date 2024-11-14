import re
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..auth.models import User
from ..auth.schemas import User as UserSchema
from .models import Hashtag, Post, post_hashtags
from .schemas import Hashtag as HashtagSchema
from .schemas import Post as PostSchema
from .schemas import PostCreate, ShowPost


# create the post service
async def create_post_svc(request: PostCreate, db: Session, user_id: int):

    db_post = Post(
        content=request.content,
        image=request.image,
        location=request.location,
        author_id=user_id,
    )
    await create_hashtags_svc(db_post, db)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


# from that post content find which one with hash and save it to the Post db
# use regex to do that
async def create_hashtags_svc(post: Post, db: Session):
    pattern = re.compile(r"#\w+")
    matches = pattern.findall(post.content)
    for match in matches:
        # removes the first # of the hashtag itself
        tags = match[1:]
        hashtag = db.query(Hashtag).filter(Hashtag.name == tags).first()
        if not hashtag:
            hashtag = Hashtag(name=tags)
            db.add(hashtag)
            try:
                db.commit()
                db.refresh(hashtag)
            except Exception as e:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )
        post.hashtags.append(hashtag)


# get users posts i.e all the posts related to a particular user
async def get_user_post_svc(user_id: int, db: Session):
    posts = (
        db.query(Post)
        .filter(Post.author_id == user_id)
        .order_by(desc(Post.created_dt))
        .all()
    )
    return [
        ShowPost(
            content=post.content,
            image=post.image,
            location=post.location,
            created_dt=post.created_dt,
            likes_count=post.likes_count,
            author=post.author.username,  # Transform the User object to a string (username)
            hashtags=post.hashtags,
            user_liked=post.user_liked,
        )
        for post in posts
    ]


# get posts from hashtags
# The optional for the list[posts schema] means it can either return an instance of that schema to validate it or None
async def get_hashtag_posts_svc(
    hash_tag_name: str, db: Session
) -> Optional[List[PostSchema]]:
    hash_tag = db.query(Hashtag).filter(Hashtag.name == hash_tag_name).first()
    if not hash_tag:
        return None
    else:
        return [PostSchema.model_validate(post) for post in hash_tag.posts]


# getting random posts for the feed part
# Use pagination to divide large set of data into smaller manageable parts/pages
async def get_random_posts_svc(
    db: Session, page: int = 1, limit: int = 10, hashtag: str = None
):
    # query for total posts count
    count_query = db.query(func.count(Post.id))
    if hashtag:
        # filter count of posts with hashtag
        count_query = count_query.join(Post.hashtags).filter(Hashtag.name == hashtag)
    # give result of the total posts based on hashtags or no hashtags scalar used for single value
    total_posts = count_query.scalar()

    # calc offset
    offset = (page - 1) * limit
    if offset >= total_posts:
        return []

    # Base query to fetch the posts
    posts_query = (
        db.query(Post, User.username).join(User).order_by(desc(Post.created_dt))
    )
    if hashtag:
        posts_query.join(Post.hashtags).filter(Hashtag.name == hashtag)

    # fetch the post with pagination now
    posts = posts_query.offset(offset).limit(limit).all()

    results = []
    # format how the results look like
    for post, username in posts:
        post_dict = post.__dict__.copy()
        # copy makes it avoid modifying the original data instead just creates new copy
        # modifies that one and data doesn't have issues
        post_dict["username"] = username
        results.append(post_dict)
    return results


# get post from post_id
async def get_post_from_id_svc(db: Session, user_id: int) -> Post:
    posts = (
        db.query(Post)
        .filter(Post.author_id == user_id)
        .order_by(desc(Post.created_dt))
        .all()
    )
    return [
        ShowPost(
            content=post.content,
            image=post.image,
            location=post.location,
            created_dt=post.created_dt,
            likes_count=post.likes_count,
            author=post.author.username,  # Transform the User object to a string (username)
            hashtags=post.hashtags,
            user_liked=post.user_liked,
        )
        for post in posts
    ]


async def delete_post_svc(db: Session, post_id: int) -> Post:
    posts = await get_post_from_id_svc(db, post_id)
    if posts:
        db.delete(posts)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Post not found")


async def like_post_svc(db: AsyncSession, post_id: int, username: str):
    post = await get_post_from_id_svc(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    user = await db.execute(select(User).where(User.username == username))
    user = user.scalars.first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user in post.user_liked:
        raise HTTPException(status_code=400, detail="User already liked this post")
    # append the user to the liked_post list of the post
    post.user_liked.append(user)
    post.likes_count = len(post.user_liked)
    # TODO logic of the activity of like
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to like post {e}")


async def unlike_post_svc(db: AsyncSession, post_id: int, username: str):
    post = await get_post_from_id_svc(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    user = await db.execute(select(User).where(User.username == username))
    user = user.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user not in post.user_liked:
        raise HTTPException(status_code=404, detail="Post wasn't liked")
    post.user_liked.remove(user)
    post.likes_count -= 1
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to like post {e}")

    # users who liked the post


async def liked_users_post_svc(db: AsyncSession, post_id: int) -> list[UserSchema]:
    # get the post first
    post = await get_post_from_id_svc(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    users_liked = post.user_liked
    # have to turn the user_liked posts to a pydantic schema
    return [UserSchema.model_validate(user) for user in users_liked]
