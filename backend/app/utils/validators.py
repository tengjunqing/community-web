"""验证工具"""

import re
from typing import Optional


def validate_username(username: str) -> bool:
    """验证用户名格式"""
    # 3-50位，字母、数字、下划线
    pattern = r"^[a-zA-Z0-9_]{3,50}$"
    return bool(re.match(pattern, username))


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """验证手机号格式（中国大陆）"""
    pattern = r"^1[3-9]\d{9}$"
    return bool(re.match(pattern, phone))


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """验证密码强度"""
    if len(password) < 6:
        return False, "密码长度至少6位"
    if len(password) > 100:
        return False, "密码长度不能超过100位"
    return True, None


def sanitize_content(content: str) -> str:
    """清理内容（防止XSS）"""
    # 移除HTML标签
    content = re.sub(r"<[^>]+>", "", content)
    # 转义特殊字符
    content = content.replace("&", "&amp;")
    content = content.replace("<", "&lt;")
    content = content.replace(">", "&gt;")
    content = content.replace('"', "&quot;")
    content = content.replace("'", "&#x27;")
    return content.strip()
