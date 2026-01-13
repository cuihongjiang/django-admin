import logging

from django.core.exceptions import ObjectDoesNotExist
from django.utils.deprecation import MiddlewareMixin
from utils.response_utils import ResponseUtils

from rest_framework.exceptions import APIException, PermissionDenied


class ExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, APIException):
            return ResponseUtils.error(msg=str(exception), code=exception.status_code)
        error_map = {
            TimeoutError: (exception.args[0], str(exception)),
            PermissionDenied: (403, '权限不足'),
            ObjectDoesNotExist: (404, '资源不存在')
        }
        error_info = error_map.get(type(exception), (500, '服务器内部错误'))
        return ResponseUtils.error(msg=error_info[1], code=error_info[0])


class ApiLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 记录API请求日志的逻辑
        pass

    def process_response(self, request, response):
        # 检查是否已渲染，未渲染则先渲染
        if hasattr(response, 'render') and callable(response.render):
            if not response.is_rendered:
                response.render()
        return response


class PerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('performance')

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except APIException as exc:  # 新增DRF异常捕获
            return ResponseUtils.error(msg=exc.detail,
                                       code=exc.status_code,
                                       status_code=exc.status_code)
        return response
