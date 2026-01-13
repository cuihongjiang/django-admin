# -*- coding: utf-8 -*-
# @Time    : 2025/10/02 17:51
# @Author  : 崔宏江
# @FileName: permission.py
# @Software: PyCharm
# -*- coding: utf-8 -*-

from rest_framework.permissions import BasePermission
from django.conf import settings # 从 django.conf 导入是最佳实践

class WhitelistOrIsAuthenticated(BasePermission):
    """
    允许访问的白名单路径，或者要求用户已认证。
    支持前缀匹配和 DEMO 模式。
    """
    def has_permission(self, request, view):
        # 1. DEMO 模式检查：允许所有只读请求
        if getattr(settings, 'DEMO', False) and request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        # 2. 白名单检查：支持前缀匹配
        path = request.path_info
        whitelist = getattr(settings, 'WHITE_LIST', [])
        if any(path.startswith(whitelist_path) for whitelist_path in whitelist):
            return True

        # 3. 用户认证检查
        user = request.user
        if not user:
            return False

        # 超级用户直接通过
        if user.is_superuser:
            return True

        # 普通用户必须已认证
        return user.is_authenticated

