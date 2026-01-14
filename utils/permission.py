# -*- coding: utf-8 -*-
# @Time    : 2025/10/02 17:51
# @Author  : 崔宏江
# @FileName: permission.py
# @Software: PyCharm
# -*- coding: utf-8 -*-

from rest_framework.permissions import BasePermission
from django.conf import settings  # 从 django.conf 导入是最佳实践


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


class IsAdminOrSuperuser(BasePermission):
    """
    只允许超级管理员或拥有 admin 角色的用户访问。
    用于需要管理员权限的操作，如：重置密码、删除用户等。
    """
    def has_permission(self, request, view):
        # 未认证用户直接拒绝
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 超级管理员允许
        if request.user.is_superuser:
            return True
        
        # 检查是否拥有 admin 角色
        return request.user.role.filter(admin=True).exists()


class IsOwnerOrAdmin(BasePermission):
    """
    允许对象的所有者或管理员访问。
    用于用户只能修改自己数据的场景。
    """
    def has_object_permission(self, request, view, obj):
        # 超级管理员允许
        if request.user.is_superuser:
            return True
        
        # 管理员角色允许
        if request.user.role.filter(admin=True).exists():
            return True
        
        # 对象所有者允许
        return obj.id == request.user.id
