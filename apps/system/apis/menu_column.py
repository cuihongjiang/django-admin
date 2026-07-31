# -*- coding: utf-8 -*-
"""
菜单列字段权限管理视图集
"""
from rest_framework.decorators import action

from apps.system.models import MenuColumnField
from apps.system.serializers import MenuColumnFieldSerializer
from utils.web.response_utils import ResponseUtils
from utils.web.viewsets import CoreModelViewSet


class MenuColumnFieldViewSet(CoreModelViewSet):
    """
    菜单列字段权限管理视图集
    CRUD + 批量创建
    """
    queryset = MenuColumnField.objects.all()
    serializer_class = MenuColumnFieldSerializer
    filter_fields = ['name', 'code', 'menu_id']

    @action(detail=False, methods=['post'], url_path='batch/create')
    def batch_create(self, request):
        """
        批量创建列字段
        POST /api/menucolumnfield/batch/create/
        请求参数: {"batch_info": [{...}, {...}]}
        """
        batch_info = request.data.get('batch_info')
        if not isinstance(batch_info, list) or not batch_info:
            return ResponseUtils.error(
                msg="batch_info 必须为非空列表", code=400, status_code=400
            )
        serializer = self.get_serializer(data=batch_info, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ResponseUtils.success(data=serializer.data, msg="批量创建成功")
