# -*- coding: utf-8 -*-
"""
操作日志视图集
"""
from apps.log.models import OperationLog
from apps.log.serializers import OperationLogSerializer
from utils.web.viewsets import CoreModelViewSet


class OperationLogViewSet(CoreModelViewSet):
    """
    操作日志视图集
    日志由 ApiLoggingMiddleware 写入，仅提供查询和删除
    """
    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer
    filter_fields = ['request_username', 'request_method', 'id']
    http_method_names = ['get', 'delete', 'head', 'options']
