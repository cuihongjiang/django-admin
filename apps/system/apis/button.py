# -*- coding: utf-8 -*-
"""
权限标识（按钮）管理视图集
"""
from apps.system.models import Button
from apps.system.serializers import ButtonSerializer
from utils.web.viewsets import CoreModelViewSet


class ButtonViewSet(CoreModelViewSet):
    """
    权限标识（按钮）管理视图集
    """
    queryset = Button.objects.all()
    serializer_class = ButtonSerializer
    filter_fields = ['name', 'code', 'id']
    # 全局配置类数据，不做行级数据权限过滤
    apply_data_permission = False
