# -*- coding: utf-8 -*-
"""
系统配置管理视图集

配置项经 apps.system.utils.system_config.get_system_config 表驱动读取（带缓存），
本视图集写入时清理 system_config:* 缓存使配置即时生效。
"""
import logging

from django.core.cache import cache

from apps.system.models import SystemConfig
from apps.system.serializers import SystemConfigSerializer
from utils.web.viewsets import CoreModelViewSet

logger = logging.getLogger(__name__)


def clear_system_config_cache(*args, **kwargs):
    try:
        cache.delete_pattern('system_config:*')
    except Exception:
        logger.warning('清理系统配置缓存失败', exc_info=True)


class SystemConfigViewSet(CoreModelViewSet):
    """
    系统配置管理视图集：key/value/status（status=False 的配置不生效，回退默认值）
    """
    # 全局配置类数据，不做行级数据权限过滤
    apply_data_permission = False
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    filter_fields = ['key', 'status', 'parent']

    def perform_create(self, serializer):
        super().perform_create(serializer)
        clear_system_config_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        clear_system_config_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        clear_system_config_cache()
