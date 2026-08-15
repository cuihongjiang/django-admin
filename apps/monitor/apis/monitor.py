# -*- coding: utf-8 -*-
"""
系统监控视图集
"""
from rest_framework.viewsets import ViewSet

from utils.web.response_utils import ResponseUtils
from apps.monitor.utils.system import system


class MonitorView(ViewSet):
    # 监控是只读接口，限制方法后路由只注册 GET /api/monitor/
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        """
        重写 list 方法，忽略默认的数据库查询，返回自定义的系统监控数据。
        """
        # 获取服务器监控数据
        qs = system().GetSystemAllInfo()

        # 直接返回你的自定义数据
        return ResponseUtils.success(data=qs, msg="接口测试成功")
