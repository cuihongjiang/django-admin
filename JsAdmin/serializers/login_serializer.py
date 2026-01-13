from rest_framework import serializers
from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        # 1. 用户认证
        user = authenticate(**data)
        if not user:
            raise serializers.ValidationError("用户名或密码错误")
        
        # 2. 用户状态检查（移到序列化器中）
        if not user.is_active:
            raise serializers.ValidationError("用户被禁用")
        
        # 3. 返回包含用户对象的已验证数据
        data['user'] = user
        return data