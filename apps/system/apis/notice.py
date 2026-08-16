# -*- coding: utf-8 -*-
"""
公告管理视图集（由低代码生成器生成）
"""
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from apps.system.models import Notice
from apps.system.serializers import NoticeSerializer
from utils.db.js_crud import export_excel, import_excel
from utils.web.response_utils import ResponseUtils
from utils.web.viewsets import CoreModelViewSet


class NoticeViewSet(CoreModelViewSet):
    """
    公告管理管理视图集
    CRUD + Excel 导入导出
    """
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    filter_fields = []
    # Excel 导入需要 multipart 上传，全局默认只开了 JSONParser
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @action(detail=False, methods=['get'], url_path='all/export')
    def all_export(self, request):
        """
        导出公告管理为 Excel
        GET /api/notice/all/export/
        """
        queryset = self.filter_queryset(self.get_queryset())
        export_fields = ['title', 'content', 'status', 'sort']
        return export_excel(queryset, NoticeSerializer, export_fields, Notice)

    @action(detail=False, methods=['post'], url_path='all/import')
    def all_import(self, request):
        """
        从 Excel 导入公告管理（multipart 上传，字段名 file）
        POST /api/notice/all/import/
        """
        file_obj = request.FILES.get('file')
        if file_obj is None:
            return ResponseUtils.error(msg="请上传 Excel 文件", code=400, status_code=400)
        import_fields = ['title', 'content', 'status', 'sort']
        count = import_excel(file_obj, Notice, import_fields, request)
        return ResponseUtils.success(msg=f"导入成功，共 {count} 条")
