# -*- coding: utf-8 -*-
"""
系统配置表驱动读取（带缓存）

- SystemConfig 中 status=True 的行生效，未配置/表不可用时返回 default
- 写入侧（SystemConfigViewSet）会清理 system_config:* 缓存，读侧另有 300s 兜底 TTL
- 读取失败（未迁移、库异常等）静默回退 default，不影响请求
"""
import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)

_MISS = object()
CACHE_TTL = 300


def get_system_config(key, default=None):
    """
    读取系统配置：get_system_config('DEMO', False)

    value 为 JSON 值（布尔/数字/字符串/对象）；行不存在、status=False 或
    表不可用时返回 default。
    """
    cache_key = f'system_config:{key}'
    try:
        value = cache.get(cache_key, _MISS)
        if value is _MISS:
            from apps.system.models import SystemConfig
            row = SystemConfig.objects.filter(key=key, status=True).order_by('id').first()
            value = row.value if row else None
            cache.set(cache_key, value, CACHE_TTL)
        return default if value is None else value
    except Exception:
        logger.warning('读取系统配置 %s 失败，回退默认值', key, exc_info=True)
        return default
