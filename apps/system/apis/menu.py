# -*- coding: utf-8 -*-
"""
菜单管理视图集
"""
from rest_framework.decorators import action

from apps.system.models import Menu
from apps.system.serializers import MenuSerializer
from utils.common.list_to_tree import list_to_route, list_to_tree
from utils.web.response_utils import ResponseUtils
from utils.web.viewsets import CoreModelViewSet


class MenuViewSet(CoreModelViewSet):
    """
    菜单管理视图集
    CRUD（列表返回树形结构）+ 当前用户路由树
    """
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    filter_fields = ['title', 'status', 'id']

    def list(self, request, *args, **kwargs):
        """菜单列表直接返回树形结构"""
        queryset = self.filter_queryset(self.get_queryset())
        menu_tree = list_to_tree(list(queryset.values()))
        return ResponseUtils.success(data=menu_tree)

    @action(detail=False, methods=['get'], url_path='route/tree')
    def route_tree(self, request):
        """
        当前用户的前端路由树
        GET /api/menu/route/tree/
        超管返回全部启用菜单，普通用户按角色关联的菜单过滤
        """
        user = request.user
        queryset = Menu.objects.filter(status=True)
        if not user.is_superuser:
            menu_ids = user.role.values_list('menu__id', flat=True)
            queryset = queryset.filter(id__in=menu_ids)
        menu_tree = list_to_route(list(queryset.values()))
        return ResponseUtils.success(data=menu_tree)
