# -*- coding: utf-8 -*-
"""
角色管理视图集
"""
from rest_framework.decorators import action

from apps.system.models import Menu, Role
from apps.system.serializers import MenuSerializer, RoleSerializer
from utils.common.list_to_tree import list_to_tree
from utils.web.response_utils import ResponseUtils
from utils.web.viewsets import CoreModelViewSet


class RoleViewSet(CoreModelViewSet):
    """
    角色管理视图集
    CRUD + 授权数据源（菜单树 / 菜单按钮树 / 菜单列字段树）
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filter_fields = ['name', 'status', 'id']
    # 全局配置类数据，不做行级数据权限过滤
    apply_data_permission = False

    @action(detail=False, methods=['get'], url_path='list/menu')
    def list_menu(self, request):
        """
        菜单树（角色授权用）
        GET /api/role/list/menu/
        """
        queryset = Menu.objects.all()
        menu_tree = list_to_tree(list(queryset.values()))
        return ResponseUtils.success(data=menu_tree)

    @action(detail=False, methods=['get'], url_path='list/menu_button')
    def list_menu_button(self, request):
        """
        菜单+按钮权限扁平列表（按钮 id 加 b 前缀，仅保留有按钮的菜单链路）
        GET /api/role/list/menu_button/
        """
        result = _collect_menu_related(
            related_name='menuPermission', id_prefix='b'
        )
        return ResponseUtils.success(data=result)

    @action(detail=False, methods=['get'], url_path='list/menu_column')
    def list_menu_column(self, request):
        """
        菜单+列字段权限扁平列表（列字段 id 加 c 前缀，仅保留有列字段的菜单链路）
        GET /api/role/list/menu_column/
        """
        result = _collect_menu_related(
            related_name='menuColumnField', id_prefix='c'
        )
        return ResponseUtils.success(data=result)


def _collect_menu_related(related_name, id_prefix):
    """
    汇总菜单及其关联对象（按钮/列字段）为扁平列表：
    关联对象 id 加前缀并挂到菜单下（parent_id 指向菜单），
    再筛选出带前缀的节点及其菜单祖先链
    """
    result = []
    for menu in Menu.objects.all():
        menu_dict = menu.__dict__.copy()
        menu_dict.pop('_state', None)

        related_list = list(getattr(menu, related_name).all().values())
        for item in related_list:
            item['id'] = f"{id_prefix}{item['id']}"
            item['parent_id'] = item.pop('menu_id')
            item['title'] = item.pop('name')

        result.extend(related_list)
        result.append(menu_dict)
    return _filter_prefixed_with_ancestors(result, id_prefix)


def _filter_prefixed_with_ancestors(data, flag):
    """筛选带前缀的节点，并向上补全其菜单祖先链"""
    return_data = []
    for item in data:
        if flag in str(item['id']):
            return_data.append(item)
            _append_ancestors(item['parent_id'], data, return_data)
    return return_data


def _append_ancestors(parent_id, data, return_data):
    """递归查找父节点并追加到结果集（去重）"""
    if parent_id is None:
        return
    for item in data:
        if parent_id == item['id'] and item not in return_data:
            return_data.append(item)
            _append_ancestors(item['parent_id'], data, return_data)
