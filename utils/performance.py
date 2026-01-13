import time
from django.utils.deprecation import MiddlewareMixin


# 响应时间中间件
class PerformanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.perf_counter()

    def process_response(self, request, response):
        duration = time.perf_counter() - request.start_time
        if 'X-Response-Time' not in response.headers:
            response.headers['X-Response-Time'] = f"{duration:.6f}s"
        return response
