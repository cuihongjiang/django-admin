# -*- coding: utf-8 -*-
# 中间件：全局异常处理（含堆栈日志）、接口操作日志入库、性能监控（慢请求）
import json
import logging
import time

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.deprecation import MiddlewareMixin

from rest_framework.exceptions import APIException, PermissionDenied

from utils.web.response_utils import ResponseUtils

logger = logging.getLogger(__name__)

# 慢请求阈值（秒），请求耗时超过该值记录 warning，可在 settings 覆盖
SLOW_REQUEST_THRESHOLD = getattr(settings, 'SLOW_REQUEST_THRESHOLD', 1.0)
# 操作日志请求体中需要脱敏的字段
SENSITIVE_FIELDS = {'password', 'old_password', 'new_password', 'confirm_password'}
# 操作日志请求体/返回信息的最大留存长度，避免超长内容撑爆字段
MAX_BODY_LENGTH = 2000


class ExceptionMiddleware(MiddlewareMixin):
    """
    全局异常兜底：统一错误响应，并将异常写入日志。
    - DRF 业务异常（APIException）属预期内，warning 级别记录
    - 其余未处理异常记录完整堆栈（error.log），便于线上排障
    """

    def process_exception(self, request, exception):
        if isinstance(exception, APIException):
            logger.warning('API 异常 %s %s: %s', request.method, request.path, exception)
            return ResponseUtils.error(msg=str(exception), code=exception.status_code)
        error_map = {
            TimeoutError: (exception.args[0] if exception.args else 504, str(exception)),
            PermissionDenied: (403, '权限不足'),
            ObjectDoesNotExist: (404, '资源不存在'),
        }
        error_info = error_map.get(type(exception), (500, '服务器内部错误'))
        # 未预期异常记录完整堆栈
        logger.error('未处理异常 %s %s: %s', request.method, request.path, exception, exc_info=True)
        return ResponseUtils.error(msg=error_info[1], code=error_info[0])


class ApiLoggingMiddleware(MiddlewareMixin):
    """
    接口操作日志中间件：将 API 操作写入 OperationLog。
    - 仅记录 API_LOG_METHODS 中声明的方法且路径以 /api/ 开头的请求
    - 请求体自动脱敏、截断
    - 日志记录失败不影响正常响应
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.enable = getattr(settings, 'API_LOG_ENABLE', False)
        self.methods = getattr(settings, 'API_LOG_METHODS', [])

    def process_response(self, request, response):
        # 检查是否已渲染，未渲染则先渲染
        if hasattr(response, 'render') and callable(response.render):
            if not response.is_rendered:
                response.render()
        try:
            self._save_operation_log(request, response)
        except Exception:
            logger.exception('操作日志记录失败')
        return response

    def _save_operation_log(self, request, response):
        if not self.enable or request.method not in self.methods:
            return
        # 仅记录后端 API 请求，跳过静态资源/文档等
        if not request.path.startswith('/api/'):
            return

        from apps.log.models import OperationLog
        from utils.web.request_util import (
            get_browser, get_os, get_request_data, get_request_ip, get_request_user,
        )

        user = get_request_user(request)
        authenticated = getattr(user, 'is_authenticated', False)
        status_code = getattr(response, 'status_code', 500)
        OperationLog.objects.create(
            request_username=getattr(user, 'username', None) if authenticated else None,
            request_ip=get_request_ip(request),
            request_method=request.method,
            request_path=request.path,
            request_body=self._safe_body(get_request_data(request)),
            request_browser=self._ua(request, get_browser),
            request_os=self._ua(request, get_os),
            response_code=str(status_code),
            status=200 <= status_code < 400,
            creator=user if authenticated else None,
            belong_dept=getattr(user, 'dept_id', None),
        )

    @staticmethod
    def _ua(request, func):
        """解析 UA 失败（如缺失 HTTP_USER_AGENT）时返回空串，不影响记录"""
        try:
            return str(func(request))
        except Exception:
            return ''

    @staticmethod
    def _safe_body(data):
        """请求体脱敏并截断"""
        if isinstance(data, dict):
            data = {k: ('***' if k in SENSITIVE_FIELDS else v) for k, v in data.items()}
        try:
            text = json.dumps(data, ensure_ascii=False)
        except (TypeError, ValueError):
            text = str(data)
        return text[:MAX_BODY_LENGTH]


class PerformanceMiddleware(MiddlewareMixin):
    """
    性能监控中间件：统计请求耗时，超过阈值记录 warning。
    并兜底捕获视图外抛出的 DRF APIException，返回统一错误响应。
    """

    def process_request(self, request):
        request._perf_start_time = time.time()

    def process_response(self, request, response):
        start = getattr(request, '_perf_start_time', None)
        if start is not None:
            cost = time.time() - start
            if cost >= SLOW_REQUEST_THRESHOLD:
                logger.warning('慢请求 %.3fs %s %s', cost, request.method, request.path)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, APIException):
            return ResponseUtils.error(
                msg=exception.detail,
                code=exception.status_code,
                status_code=exception.status_code,
            )
        return None
