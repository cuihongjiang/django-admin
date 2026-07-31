# -*- coding: utf-8 -*-
"""
分类字典管理视图集
"""
from rest_framework.decorators import action

from apps.data_dict.models import CategoryDict
from apps.data_dict.serializers import CategoryDictSerializer
from utils.common.list_to_tree import list_to_tree
from utils.web.response_utils import ResponseUtils
from utils.web.viewsets import CoreModelViewSet


class CategoryDictViewSet(CoreModelViewSet):
    """
    分类字典管理视图集
    CRUD + 分类树
    """
    queryset = CategoryDict.objects.all()
    serializer_class = CategoryDictSerializer
    filter_fields = ['label', 'value', 'code']

    @action(detail=False, methods=['get'], url_path='list/tree')
    def list_tree(self, request):
        """
        分类字典树
        GET /api/categorydict/list/tree/
        """
        queryset = self.filter_queryset(self.get_queryset())
        category_dict_tree = list_to_tree(list(queryset.values()))
        return ResponseUtils.success(data=category_dict_tree)
