# -*- coding: utf-8 -*-
"""
日志域序列化器：登录日志 / 操作日志
"""
from apps.log.models import LoginLog, OperationLog
from utils.web.serializers import CoreModelSerializer


class LoginLogSerializer(CoreModelSerializer):
    class Meta(CoreModelSerializer.Meta):
        model = LoginLog
        fields = '__all__'


class OperationLogSerializer(CoreModelSerializer):
    class Meta(CoreModelSerializer.Meta):
        model = OperationLog
        fields = '__all__'


__all__ = ["LoginLogSerializer", "OperationLogSerializer"]
