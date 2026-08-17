# -*- coding: utf-8 -*-
"""
接口白名单管理视图集

白名单在 settings.WHITE_LIST 的基础上叠加本表配置（前缀匹配），
认证类 WhitelistOrIsAuthenticated 通过缓存读取，本视图集写入时清理缓存。
"""
import logging

from django.core.cache import cache

from apps.system.models import ApiWhiteList
from apps.system.serializers import ApiWhiteListSerializer
from utils.web.viewsets import CoreModelViewSet

logger = logging.getLogger(__name__)

WHITE_LIST_CACHE_KEY = 'api_white_list'


def clear_white_list_cache(*args, **kwargs):
    try:
        cache.delete(WHITE_LIST_CACHE_KEY)
    except Exception:
        logger.warning('清理接口白名单缓存失败', exc_info=True)


class ApiWhiteListViewSet(CoreModelViewSet):
    """
    接口白名单管理视图集

    - url：前缀匹配，如 /api/login/ 放行整个登录模块
    - method：留空放行全部方法，否则仅放行对应方法
    """
    # 全局配置类数据，不做行级数据权限过滤
    apply_data_permission = False
    queryset = ApiWhiteList.objects.all()
    serializer_class = ApiWhiteListSerializer
    filter_fields = ['url', 'method']

    def perform_create(self, serializer):
        super().perform_create(serializer)
        clear_white_list_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        clear_white_list_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        clear_white_list_cache()
