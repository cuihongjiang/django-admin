# -*- coding: utf-8 -*-
# @Time    : 2026/07/31 10:00
# @Author  : 崔宏江
# @FileName: viewsets.py
# @Software: PyCharm
# -*- coding: utf-8 -*-
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from utils.web.pagination import MyPagination
from utils.web.response_utils import ResponseUtils


class CoreModelViewSet(ModelViewSet):
    """
    标准化 ModelViewSet 基类
    - 统一 ResponseUtils 响应格式
    - filter_fields 声明查询参数精确过滤字段
    - list 带 page 参数时分页，否则返回全量
    - 创建/更新时自动填充审计字段（creator/modifier/belong_dept）
    """
    pagination_class = MyPagination
    filter_fields = []

    def filter_queryset(self, queryset):
        """按 filter_fields 声明的字段做查询参数精确过滤，空值跳过"""
        queryset = super().filter_queryset(queryset)
        for field in self.filter_fields:
            value = self.request.query_params.get(field)
            if value not in (None, ''):
                queryset = queryset.filter(**{field: value})
        return queryset

    def perform_create(self, serializer):
        """创建时自动填充审计字段"""
        user = self.request.user
        serializer.save(
            creator=user if getattr(user, 'is_authenticated', False) else None,
            modifier=getattr(user, 'username', None),
            belong_dept=getattr(user, 'dept_id', None),
        )

    def perform_update(self, serializer):
        """更新时自动记录修改人"""
        serializer.save(modifier=getattr(self.request.user, 'username', None))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ResponseUtils.success(data=serializer.data, msg="创建成功")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ResponseUtils.success(data=serializer.data, msg="更新成功")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ResponseUtils.success(msg="删除成功")

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return ResponseUtils.success(data=serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # 带 page 参数时分页，兼容不分页的全量拉取
        if request.query_params.get('page'):
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return ResponseUtils.success(data={
                    'items': serializer.data,
                    'total': self.paginator.page.paginator.count,
                })
        serializer = self.get_serializer(queryset, many=True)
        return ResponseUtils.success(data=serializer.data)

    @action(detail=False, methods=['get'], url_path='all/list')
    def all_list(self, request):
        """不分页返回全部数据，用于下拉选项等场景"""
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return ResponseUtils.success(data=serializer.data)
