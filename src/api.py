from fastapi import APIRouter
from .auth.views import router as auth_router
from .post.views import router as post_router


router = APIRouter(prefix="/v1")  # the version of the API

router.include_router(auth_router)
router.include_router(post_router)
