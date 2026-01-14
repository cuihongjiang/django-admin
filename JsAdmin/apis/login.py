# -*- coding: utf-8 -*-
# @Time    : 2025/09/27 17:43
# @Author  : 崔宏江
# @FileName: login.py
# @Software: PyCharm
# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.conf import settings
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from utils.response_utils import ResponseUtils
from JsAdmin.serializers import user_serializers, login_serializer


class LoginViewSet(ViewSet):
    """
    登录认证视图集
    提供用户登录和 token 刷新功能
    """
    
    def create(self, request, *args, **kwargs):
        """
        用户登录接口
        POST /api/login/
        """
        # 1. 验证登录数据
        serializer = login_serializer.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = validated_data['user']

        # 2. 生成 JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # 3. 缓存 accessToken
        cache.set(
            f"user_token:{user.id}", 
            access_token, 
            timeout=settings.PERMISSION_CACHE_TIMEOUT
        )

        # 4. 返回登录信息
        return ResponseUtils.success({
            "accessToken": access_token,
            "refreshToken": str(refresh),
            "user": user_serializers.SchemaOut(user).data
        })

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
            # 1. 验证 refreshToken
            refresh = RefreshToken(refresh_token)
            user_id = refresh.get('user_id')
            
            # 2. 生成新的 accessToken
            new_access_token = str(refresh.access_token)
            
            # 3. token 轮换：生成新的 refreshToken
            if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
                refresh.set_jti()
                refresh.set_exp()
                new_refresh_token = str(refresh)
            else:
                new_refresh_token = refresh_token
            
            # 4. 更新缓存
            cache.set(
                f"user_token:{user_id}", 
                new_access_token, 
                timeout=settings.PERMISSION_CACHE_TIMEOUT
            )
            
            # 5. 返回新 token
            return ResponseUtils.success({
                "accessToken": new_access_token,
                "refreshToken": new_refresh_token
            })
            
        except TokenError:
            return ResponseUtils.error(
                msg="refreshToken 无效或已过期", 
                code=401, 
                status_code=401
            )
        except Exception as e:
            return ResponseUtils.error(
                msg=f"token 刷新失败: {str(e)}", 
                code=500, 
                status_code=500
            )