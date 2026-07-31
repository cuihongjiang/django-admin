# -*- coding: utf-8 -*-
"""
登录日志视图集
"""
from apps.log.models import LoginLog
from apps.log.serializers import LoginLogSerializer
from utils.web.viewsets import CoreModelViewSet


class LoginLogViewSet(CoreModelViewSet):
    """
    登录日志视图集
    日志由登录流程写入，仅提供查询和删除
    """
    queryset = LoginLog.objects.all()
    serializer_class = LoginLogSerializer
    filter_fields = ['username', 'ip', 'id']
    http_method_names = ['get', 'delete', 'head', 'options']
