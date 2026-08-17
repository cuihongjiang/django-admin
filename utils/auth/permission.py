# -*- coding: utf-8 -*-
# @Time    : 2025/10/02 17:51
# @Author  : 崔宏江
# @FileName: permission.py
# @Software: PyCharm
# -*- coding: utf-8 -*-

import logging

from rest_framework.permissions import BasePermission
from django.conf import settings  # 从 django.conf 导入是最佳实践

logger = logging.getLogger(__name__)


class WhitelistOrIsAuthenticated(BasePermission):
    """
    允许访问的白名单路径，或者要求用户已认证。

    白名单来源 = settings.WHITE_LIST + 接口白名单表（system_api_white_list，页面可管理），
    均为前缀匹配；表条目配置了 method 时仅放行对应方法（HEAD/OPTIONS 视同 GET）。
    结果缓存 300s，白名单表写入时清理。支持 DEMO 模式（表驱动开关）。
    """
    # 请求方法 -> MenuButton/ApiWhiteList 同款 METHOD_CHOICES
    METHOD_MAP = {'GET': 0, 'HEAD': 0, 'OPTIONS': 0, 'POST': 1, 'PUT': 2, 'DELETE': 3}
    WHITE_LIST_CACHE_KEY = 'api_white_list'
    WHITE_LIST_CACHE_TTL = 300

    @classmethod
    def get_whitelist_entries(cls):
        """
        白名单条目集合 [(path, method_int_or_None), ...]，带缓存
        """
        from django.core.cache import cache

        try:
            entries = cache.get(cls.WHITE_LIST_CACHE_KEY)
            if entries is None:
                from apps.system.models import ApiWhiteList
                rows = ApiWhiteList.objects.exclude(url='').values_list('url', 'method')
                entries = [(path, None) for path in getattr(settings, 'WHITE_LIST', []) if path]
                entries += [(path, method) for path, method in rows]
                cache.set(cls.WHITE_LIST_CACHE_KEY, entries, cls.WHITE_LIST_CACHE_TTL)
            return entries
        except Exception:
            logger.warning('读取接口白名单表失败，仅使用 settings 白名单', exc_info=True)
            return [(path, None) for path in getattr(settings, 'WHITE_LIST', []) if path]

    def has_permission(self, request, view):
        # 1. DEMO 模式检查（表驱动开关）：允许所有只读请求
        from apps.system.utils.system_config import get_system_config
        if get_system_config('DEMO', getattr(settings, 'DEMO', False)) and \
                request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        # 2. 白名单检查：前缀匹配，表条目可限定方法
        path = request.path_info
        method_int = self.METHOD_MAP.get(request.method)
        for whitelist_path, whitelist_method in self.get_whitelist_entries():
            if path.startswith(whitelist_path) and (whitelist_method is None or
                                                    whitelist_method == method_int):
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
        allowed = request.user.role.filter(admin=True).exists()
        if not allowed:
            logger.warning('权限拒绝（需管理员）username=%s %s %s',
                           request.user.username, request.method, request.path)
        return allowed


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
        allowed = obj.id == request.user.id
        if not allowed:
            logger.warning('权限拒绝（非本人或管理员）username=%s %s %s',
                           request.user.username, request.method, request.path)
        return allowed
