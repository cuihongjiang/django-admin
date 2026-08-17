# -*- coding: utf-8 -*-
"""
信号：数据权限缓存失效

DataPermissionMixin 会把用户的 data_range 缓存到 user_data_range:{user_id}，
角色本身变化、用户的角色关联变化时必须清理，否则权限调整最长 1 小时后才生效。
"""
import logging

from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def clear_data_range_cache(*args, **kwargs):
    try:
        cache.delete_pattern('user_data_range:*')
    except Exception:
        # 非 django-redis 后端不支持 delete_pattern，等 TTL 自然过期
        logger.warning('清理 user_data_range 缓存失败', exc_info=True)


def register():
    from apps.system.models import Role, Users

    post_save.connect(clear_data_range_cache, sender=Role)
    post_delete.connect(clear_data_range_cache, sender=Role)
    m2m_changed.connect(clear_data_range_cache, sender=Users.role.through)
