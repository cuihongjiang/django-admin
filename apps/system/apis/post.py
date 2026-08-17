# -*- coding: utf-8 -*-
"""
岗位管理视图集
"""
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from apps.system.models import Post
from apps.system.serializers import PostSerializer
from utils.db.js_crud import export_excel, import_excel
from utils.web.response_utils import ResponseUtils
from utils.web.viewsets import CoreModelViewSet


class PostViewSet(CoreModelViewSet):
    """
    岗位管理视图集
    CRUD + Excel 导入导出
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_fields = ['name', 'code', 'status', 'id']
    # 全局配置类数据，不做行级数据权限过滤
    apply_data_permission = False
    # all/import 需要 multipart 上传 Excel，全局默认只开了 JSONParser
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @action(detail=False, methods=['get'], url_path='all/export')
    def all_export(self, request):
        """
        导出岗位为 Excel
        GET /api/position/all/export/
        """
        queryset = self.filter_queryset(self.get_queryset())
        export_fields = ['name', 'code', 'status', 'sort']
        return export_excel(queryset, PostSerializer, export_fields, Post)

    @action(detail=False, methods=['post'], url_path='all/import')
    def all_import(self, request):
        """
        从 Excel 导入岗位（multipart 上传，字段名 file）
        POST /api/position/all/import/
        """
        file_obj = request.FILES.get('file')
        if file_obj is None:
            return ResponseUtils.error(msg="请上传 Excel 文件", code=400, status_code=400)
        import_fields = ['name', 'code', 'status', 'sort']
        count = import_excel(file_obj, Post, import_fields, request)
        return ResponseUtils.success(msg=f"导入成功，共 {count} 条")
