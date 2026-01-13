# utils/response_utils.py
from rest_framework.response import Response


class ResponseUtils:
    @staticmethod
    def success(data=None, msg='操作成功', status_code=200):
        return Response({
            "code": 2000,
            "result": data,
            "message": msg,
            "success": True
        }, status=status_code)

    @staticmethod
    def error(msg='操作失败', code=500, status_code=500):
        return Response({
            "code": code,
            "result": None,
            "message": msg,
            "success": False
        }, status=status_code)

    @staticmethod
    def validation_error(msg='参数验证失败', code=400, status_code=400):
        return Response({
            "code": code,
            "result": None,
            "message": msg,
            "success": False
        }, status=status_code)

    @staticmethod
    def not_found(msg='资源不存在', code=404, status_code=404):
        return Response({
            "code": code,
            "result": None,
            "message": msg,
            "success": False
        }, status=status_code)

    @staticmethod
    def permission_denied(msg='权限不足', code=403, status_code=403):
        return Response({
            "code": code,
            "result": None,
            "message": msg,
            "success": False
        }, status=status_code)

    @staticmethod
    def unauthorized(msg='身份验证失败', code=401, status_code=401):
        return Response({
            "code": code,
            "result": None,
            "message": msg,
            "success": False
        }, status=status_code)
