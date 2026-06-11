"""文件上传工具"""

import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from PIL import Image

from app.config import settings


async def upload_image(file: UploadFile, directory: str = "avatars") -> str:
    """上传图片"""
    # 检查文件类型
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名为空"
        )

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，允许的类型：{', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # 检查文件大小
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制，最大允许 {settings.MAX_FILE_SIZE // 1024 // 1024}MB"
        )

    # 创建上传目录
    upload_dir = os.path.join(settings.UPLOAD_DIR, directory)
    os.makedirs(upload_dir, exist_ok=True)

    # 生成唯一文件名
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(upload_dir, filename)

    # 保存文件
    with open(filepath, "wb") as f:
        f.write(content)

    # 验证图片是否有效
    try:
        with Image.open(filepath) as img:
            img.verify()
    except Exception:
        # 删除无效文件
        os.remove(filepath)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的图片文件"
        )

    # 返回相对路径
    return f"/uploads/{directory}/{filename}"


def delete_file(filepath: str) -> bool:
    """删除文件"""
    try:
        # 转换为绝对路径
        abs_path = filepath.lstrip("/")
        if os.path.exists(abs_path):
            os.remove(abs_path)
            return True
    except Exception:
        pass
    return False
