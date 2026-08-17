# -*- coding: utf-8 -*-
"""
菜单按钮权限管理视图集
"""
from apps.system.models import MenuButton
from apps.system.serializers import MenuButtonSerializer
from utils.web.viewsets import CoreModelViewSet


class MenuButtonViewSet(CoreModelViewSet):
    """
    菜单按钮权限管理视图集
    """
    queryset = MenuButton.objects.all()
    serializer_class = MenuButtonSerializer
    filter_fields = ['name', 'code', 'menu_id']
    # 全局配置类数据，不做行级数据权限过滤
    apply_data_permission = False
