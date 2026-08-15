# -*- coding: utf-8 -*-
"""
[[ name ]]视图集（由低代码生成器生成）
"""
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from apps.[[ app_label ]].models import [[ model_name ]]
from apps.[[ app_label ]].serializers import [[ model_name ]]Serializer
from utils.db.js_crud import export_excel, import_excel
from utils.web.response_utils import ResponseUtils
from utils.web.viewsets import CoreModelViewSet


class [[ model_name ]]ViewSet(CoreModelViewSet):
    """
    [[ name ]]管理视图集
    CRUD + Excel 导入导出
    """
    queryset = [[ model_name ]].objects.all()
    serializer_class = [[ model_name ]]Serializer
    filter_fields = [[ search_fields|pylist ]]
    # Excel 导入需要 multipart 上传，全局默认只开了 JSONParser
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @action(detail=False, methods=['get'], url_path='all/export')
    def all_export(self, request):
        """
        导出[[ name ]]为 Excel
        GET /api/[[ code ]]/all/export/
        """
        queryset = self.filter_queryset(self.get_queryset())
        export_fields = [[ export_fields|pylist ]]
        return export_excel(queryset, [[ model_name ]]Serializer, export_fields, [[ model_name ]])

    @action(detail=False, methods=['post'], url_path='all/import')
    def all_import(self, request):
        """
        从 Excel 导入[[ name ]]（multipart 上传，字段名 file）
        POST /api/[[ code ]]/all/import/
        """
        file_obj = request.FILES.get('file')
        if file_obj is None:
            return ResponseUtils.error(msg="请上传 Excel 文件", code=400, status_code=400)
        import_fields = [[ export_fields|pylist ]]
        count = import_excel(file_obj, [[ model_name ]], import_fields, request)
        return ResponseUtils.success(msg=f"导入成功，共 {count} 条")
