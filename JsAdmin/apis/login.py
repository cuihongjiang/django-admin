# -*- coding: utf-8 -*-
# @Time    : 2025/09/27 17:43
# @Author  : 崔宏江
# @FileName: login.py
# @Software: PyCharm
# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.conf import settings
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from utils.response_utils import ResponseUtils
from JsAdmin.serializers import user_serializers, login_serializer


class LoginView(ModelViewSet):
    serializer_class = login_serializer.LoginSerializer

    def create(self, request, *args, **kwargs):
        # 1. 使用序列化器验证输入数据和认证
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = validated_data['user']

        # 2. JWT生成与缓存（业务逻辑保留在视图层）
        refresh = RefreshToken.for_user(user)
        cache.set(f"user_token:{user.id}", str(refresh.access_token), timeout=settings.PERMISSION_CACHE_TIMEOUT)

        # 3. 格式化响应数据
        return ResponseUtils.success({
            "accessToken": str(refresh.access_token),
            "refreshToken": str(refresh),
            "user": user_serializers.SchemaOut(user).data
        })