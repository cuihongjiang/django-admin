# -*- coding: utf-8 -*-
"""
系统管理域序列化器：部门 / 岗位 / 角色 / 菜单 / 菜单权限 / 菜单列字段 / 权限标识 / 用户
"""
from apps.system.models import Button, Dept, Menu, MenuButton, MenuColumnField, Post, Role
from utils.web.serializers import CoreModelSerializer

# 用户读写序列化器较特殊（读写分离 + 自定义 create/update），单独成文件后在此汇总导出
from apps.system.serializers.user import SchemaIn, SchemaOut


class DeptSerializer(CoreModelSerializer):
    class Meta(CoreModelSerializer.Meta):
        model = Dept
        fields = '__all__'


class PostSerializer(CoreModelSerializer):
    class Meta(CoreModelSerializer.Meta):
        model = Post
        fields = '__all__'


class RoleSerializer(CoreModelSerializer):
    """角色序列化器，menu/permission/dept/column 多对多关系由 DRF 自动 set"""

    class Meta(CoreModelSerializer.Meta):
        model = Role
        fields = '__all__'


class MenuSerializer(CoreModelSerializer):
    class Meta(CoreModelSerializer.Meta):
        model = Menu
        fields = '__all__'


class MenuButtonSerializer(CoreModelSerializer):
    class Meta(CoreModelSerializer.Meta):
        model = MenuButton
        fields = '__all__'


class MenuColumnFieldSerializer(CoreModelSerializer):
    class Meta(CoreModelSerializer.Meta):
        model = MenuColumnField
        fields = '__all__'


class ButtonSerializer(CoreModelSerializer):
    class Meta(CoreModelSerializer.Meta):
        model = Button
        fields = '__all__'


__all__ = [
    "DeptSerializer",
    "PostSerializer",
    "RoleSerializer",
    "MenuSerializer",
    "MenuButtonSerializer",
    "MenuColumnFieldSerializer",
    "ButtonSerializer",
    "SchemaIn",
    "SchemaOut",
]
