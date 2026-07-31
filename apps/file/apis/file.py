# -*- coding: utf-8 -*-
"""
文件管理视图集
"""
import hashlib
import logging

from django.http import FileResponse
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from apps.file.models import File
from apps.file.serializers import FileSerializer
from utils.web.response_utils import ResponseUtils
from utils.web.viewsets import CoreModelViewSet

logger = logging.getLogger(__name__)


class FileViewSet(CoreModelViewSet):
    """
    文件管理视图集
    查询/删除 + 上传（md5 去重秒传）/ 下载 / 图片预览
    """
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filter_fields = ['name', 'md5sum']
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        上传文件（multipart 上传，字段名 file）
        POST /api/file/upload/
        按 md5 去重：同内容文件直接复用已有记录（秒传）
        """
        file_obj = request.FILES.get('file')
        if file_obj is None:
            return ResponseUtils.error(msg="请上传文件", code=400, status_code=400)

        # 计算 md5，同内容文件不重复落盘
        md5 = hashlib.md5()
        for chunk in file_obj.chunks():
            md5.update(chunk)
        md5sum = md5.hexdigest()

        existed = File.objects.filter(md5sum=md5sum).first()
        if existed is not None:
            serializer = self.get_serializer(existed)
            logger.info('文件秒传 name=%s md5=%s operator=%s',
                        file_obj.name, md5sum, getattr(request.user, 'username', None))
            return ResponseUtils.success(data=serializer.data, msg="上传成功（秒传）")

        file_obj.seek(0)
        user = request.user
        instance = File(
            name=file_obj.name,
            save_name=file_obj.name,
            size=file_obj.size,
            md5sum=md5sum,
            url=file_obj,
            creator=user if getattr(user, 'is_authenticated', False) else None,
            modifier=getattr(user, 'username', None),
            belong_dept=getattr(user, 'dept_id', None),
        )
        instance.save()
        serializer = self.get_serializer(instance)
        logger.info('文件上传 name=%s size=%s md5=%s operator=%s',
                    file_obj.name, file_obj.size, md5sum, getattr(user, 'username', None))
        return ResponseUtils.success(data=serializer.data, msg="上传成功")

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        下载文件
        GET /api/file/{id}/download/
        """
        instance = self.get_object()
        return FileResponse(
            instance.url.open('rb'),
            as_attachment=True,
            filename=instance.name or instance.save_name,
        )

    @action(detail=True, methods=['get'])
    def image(self, request, pk=None):
        """
        图片预览（内联展示，不触发下载）
        GET /api/file/{id}/image/
        """
        instance = self.get_object()
        return FileResponse(instance.url.open('rb'))
