# -*- coding: utf-8 -*-
"""
字典项管理视图集
"""
from rest_framework import serializers
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.data_dict.models import Dict, DictItem
from apps.data_dict.serializers import DictItemSerializer
from utils.web.response_utils import ResponseUtils
from utils.web.viewsets import CoreModelViewSet


class DictItemViewSet(CoreModelViewSet):
    """
    字典项管理视图集
    CRUD + 按字典编码查询字典项
    """
    queryset = DictItem.objects.all()
    serializer_class = DictItemSerializer
    filter_fields = ['label', 'value', 'dict_id', 'status']
    # 全局配置类数据，不做行级数据权限过滤
    apply_data_permission = False

    @extend_schema(parameters=[OpenApiParameter(name='code', type=str, location='query', description='字典编码')])
    @action(detail=False, methods=['get'], url_path='by/code')
    def by_code(self, request):
        """
        按字典编码查询启用的字典项
        GET /api/dictitem/by/code/?code=xxx
        """
        code = request.query_params.get('code')
        if not code:
            return ResponseUtils.error(msg="code 参数不能为空", code=400, status_code=400)
        dict_obj = Dict.objects.filter(code=code, status=True).first()
        if dict_obj is None:
            return ResponseUtils.success(data=[])
        items = dict_obj.dictItem.filter(status=True)
        serializer = self.get_serializer(items, many=True)
        return ResponseUtils.success(data=serializer.data)
