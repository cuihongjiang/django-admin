# -*- coding: utf-8 -*-
"""
用户序列化器（读写分离：SchemaIn 写 / SchemaOut 读）
"""
from rest_framework import serializers

from apps.system.models import Users


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
