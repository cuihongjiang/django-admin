# -*- coding: utf-8 -*-
"""
登录认证视图集
"""
import logging

from django.conf import settings
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema

from utils.auth.authentication import blacklist_token, is_token_revoked
from utils.web.request_util import get_request_ip, save_login_log
from utils.web.response_utils import ResponseUtils
from apps.auth.serializers import LoginSerializer
from apps.system.serializers import SchemaOut

logger = logging.getLogger(__name__)


class RefreshTokenIn(serializers.Serializer):
    """刷新 token 请求体（仅用于接口文档声明）"""
    refreshToken = serializers.CharField(help_text='登录时返回的 refreshToken')


class LogoutIn(serializers.Serializer):
    """退出登录请求体（仅用于接口文档声明）"""
    refreshToken = serializers.CharField(required=False, help_text='需要一并吊销的 refreshToken')


class LoginViewSet(GenericViewSet):
    """
    登录认证视图集
    提供用户登录和 token 刷新功能
    """
    serializer_class = LoginSerializer

    def get_serializer_class(self):
        # 各 action 的请求体声明见方法上的 extend_schema
        return LoginSerializer

    def create(self, request, *args, **kwargs):
        """
        用户登录接口
        POST /api/login/
        """
        ip = get_request_ip(request)
        # 1. 验证登录数据
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            username = request.data.get('username')
            logger.warning('登录失败 username=%s ip=%s: %s', username, ip, serializer.errors)
            detail = serializer.errors.get('non_field_errors') or ['用户名或密码错误']
            return ResponseUtils.error(msg=str(detail[0]), code=400, status_code=400)
        validated_data = serializer.validated_data
        user = validated_data['user']

        # 2. 生成 JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # 3. 记录登录审计（登录日志入库失败不影响登录）
        logger.info('登录成功 username=%s ip=%s', user.username, ip)
        request.user = user
        try:
            save_login_log(request)
        except Exception:
            logger.exception('登录日志记录失败 username=%s', user.username)

        # 4. 返回登录信息
        return ResponseUtils.success({
            "accessToken": access_token,
            "refreshToken": str(refresh),
            "user": SchemaOut(user).data
        })

    @extend_schema(request=RefreshTokenIn)
    @action(detail=False, methods=["POST"])
    def refresh(self, request, *args, **kwargs):
        """
        刷新 token 接口
        POST /api/login/refresh/
        接收 refreshToken，返回新的 accessToken 和 refreshToken
        """
        refresh_token = request.data.get("refreshToken")
        
        if not refresh_token:
            return ResponseUtils.error(
                msg="缺少 refreshToken 参数", 
                code=400, 
                status_code=400
            )
        
        try:
            # 1. 验证 refreshToken（签名/有效期），并检查是否已被吊销
            #    （单 token 黑名单 + 用户级失效水位线）
            refresh = RefreshToken(refresh_token)
            if is_token_revoked(refresh):
                return ResponseUtils.error(
                    msg="refreshToken 已被吊销",
                    code=401,
                    status_code=401
                )

            # 2. 生成新的 accessToken
            new_access_token = str(refresh.access_token)
            
            # 3. token 轮换：旧 refreshToken 拉黑后生成新的 refreshToken
            if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
                blacklist_token(refresh)
                refresh.set_jti()
                refresh.set_exp()
                new_refresh_token = str(refresh)
            else:
                new_refresh_token = refresh_token
            
            # 4. 返回新 token
            return ResponseUtils.success({
                "accessToken": new_access_token,
                "refreshToken": new_refresh_token
            })
            
        except TokenError:
            logger.warning('刷新 token 失败：refreshToken 无效或已过期')
            return ResponseUtils.error(
                msg="refreshToken 无效或已过期", 
                code=401, 
                status_code=401
            )
        except Exception as e:
            logger.exception('刷新 token 异常')
            return ResponseUtils.error(
                msg=f"token 刷新失败: {str(e)}", 
                code=500, 
                status_code=500
            )

    @extend_schema(request=LogoutIn)
    @action(detail=False, methods=["POST"])
    def logout(self, request, *args, **kwargs):
        """
        退出登录接口
        POST /api/login/logout/
        将当前 accessToken 和请求体中的 refreshToken 加入 Redis 黑名单，
        使其立即失效（仅影响当前端，不影响其他端的登录状态）
        """
        # 1. 吊销 Authorization 头中的 accessToken
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            try:
                blacklist_token(AccessToken(auth_header.split(' ')[1]))
            except TokenError:
                logger.debug('注销时 accessToken 已过期或无效，无需吊销')

        # 2. 吊销请求体中的 refreshToken
        refresh_token = request.data.get("refreshToken")
        if refresh_token:
            try:
                blacklist_token(RefreshToken(refresh_token))
            except TokenError:
                logger.debug('注销时 refreshToken 已过期或无效，无需吊销')

        logger.info('退出登录 username=%s ip=%s',
                    getattr(request.user, 'username', None), get_request_ip(request))
        return ResponseUtils.success(msg="退出成功")
