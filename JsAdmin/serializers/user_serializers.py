# -*- coding: utf-8 -*-
# @Time    : 2025/09/20 1:31
# @Author  : 崔宏江
# @FileName: user_serializers.py
# @Software: PyCharm
# -*- coding: utf-8 -*-
from rest_framework import serializers
from JsAdmin.models import Users, Post, Role, Dept

"""
主要用于将复杂的数据类型（如 Django 模型实例）转换为 Python 数据类型（如字典），
以便进一步转换为 JSON、XML 等格式，同时也可以将解析后的数据（如 JSON）转换回复杂的数据类型（如 Django 模型实例）。
序列化器在数据的序列化和反序列化过程中起到了桥梁的作用。
"""

class SchemaIn(serializers.ModelSerializer):
    dept_id = serializers.IntegerField(source="dept.id", required=False)
    post = serializers.ListField(child=serializers.IntegerField(), required=False)
    role = serializers.ListField(child=serializers.IntegerField(), required=False)

    class Meta:
        model = Users
        fields = ["username", "email", "mobile", "dept_id", "post", "role"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password", "123456")
        user = Users.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == "post":
                instance.post.set(value)
            elif attr == "role":
                instance.role.set(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class SchemaOut(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ["id", "username", "email", "mobile", "dept_id", "post", "role"]
        extra_kwargs = {
            "password": {"write_only": True},
        }
