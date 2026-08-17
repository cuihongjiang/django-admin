# -*- coding: utf-8 -*-
"""
部门管理视图集
"""
from rest_framework.decorators import action

from apps.system.models import Dept
from apps.system.serializers import DeptSerializer
from utils.common.list_to_tree import list_to_tree
from utils.web.response_utils import ResponseUtils
from utils.web.viewsets import CoreModelViewSet


class DeptViewSet(CoreModelViewSet):
    """
    部门管理视图集
    CRUD + 部门树
    """
    queryset = Dept.objects.all()
    serializer_class = DeptSerializer
    filter_fields = ['name', 'status', 'id']
    # 全局配置类数据，不做行级数据权限过滤
    apply_data_permission = False

    @action(detail=False, methods=['get'], url_path='list/tree')
    def list_tree(self, request):
        """
        部门树
        GET /api/department/list/tree/
        """
        queryset = self.filter_queryset(self.get_queryset())
        dept_tree = list_to_tree(list(queryset.values()))
        return ResponseUtils.success(data=dept_tree)
