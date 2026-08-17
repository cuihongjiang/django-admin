# -*- coding: utf-8 -*-
"""
字典管理视图集
"""
from apps.data_dict.models import Dict
from apps.data_dict.serializers import DictSerializer
from utils.web.viewsets import CoreModelViewSet


class DictViewSet(CoreModelViewSet):
    """
    字典管理视图集
    """
    queryset = Dict.objects.all()
    serializer_class = DictSerializer
    filter_fields = ['name', 'code', 'status', 'id']
    # 全局配置类数据，不做行级数据权限过滤
    apply_data_permission = False
