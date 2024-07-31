from fastapi import APIRouter
from .auth.views import router as auth_router


router = APIRouter(prefix="/v1")  # the version of the API

router.include_router(auth_router)