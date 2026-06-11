"""API v1 模块"""

from fastapi import APIRouter

from app.api.v1 import auth, users, posts, messages, groups

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(posts.router, prefix="/posts", tags=["动态"])
api_router.include_router(messages.router, prefix="/messages", tags=["私信"])
api_router.include_router(groups.router, prefix="/groups", tags=["群组"])
