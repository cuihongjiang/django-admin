from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from utils.response_utils import ResponseUtils
from utils.system import system


class MonitorView(ModelViewSet):
    def list(self, request, *args, **kwargs):
        """
        重写 list 方法，忽略默认的数据库查询，返回自定义的系统监控数据。
        """
        # 获取服务器监控数据
        qs = system().GetSystemAllInfo()

        # 直接返回你的自定义数据
        return ResponseUtils.success(data=qs, msg="接口测试成功")