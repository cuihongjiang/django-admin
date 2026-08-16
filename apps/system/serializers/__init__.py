# -*- coding: utf-8 -*-
"""
系统管理域序列化器：部门 / 岗位 / 角色 / 菜单 / 菜单权限 / 菜单列字段 / 权限标识 / 用户
"""
import json

from rest_framework import serializers

from apps.system.models import Button, Dept, Menu, MenuButton, MenuColumnField, Post, Role, GeneratorTemplate
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
        # 新建角色时通常先不关联任何菜单/部门，M2M 字段必须允许缺省
        extra_kwargs = {
            'dept': {'required': False},
            'menu': {'required': False},
            'permission': {'required': False},
            'column': {'required': False},
        }


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


class JSONObjectListField(serializers.JSONField):
    """
    TextField 存 JSON 的读写转换：
    入参 list/dump-str -> json.dumps 字符串入库；出参 -> json.loads 还原为数组
    """
    def to_internal_value(self, data):
        if not isinstance(data, str):
            return json.dumps(data, ensure_ascii=False)
        # 字符串入参也统一规范为合法 JSON 后存储
        json.loads(data)
        return data

    def to_representation(self, value):
        if isinstance(value, (list, dict)):
            return value
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return []


class GeneratorTemplateSerializer(CoreModelSerializer):
    """
    代码生成器模板序列化器

    form_info / table_info 在库中是 JSON 字符串，对外接口直接收发数组
    """
    form_info = JSONObjectListField()
    table_info = JSONObjectListField()

    class Meta(CoreModelSerializer.Meta):
        model = GeneratorTemplate
        fields = '__all__'


__all__ = [
    "DeptSerializer",
    "PostSerializer",
    "RoleSerializer",
    "MenuSerializer",
    "MenuButtonSerializer",
    "MenuColumnFieldSerializer",
    "ButtonSerializer",
    "GeneratorTemplateSerializer",
    "SchemaIn",
    "SchemaOut",
]


# -*- coding: utf-8 -*-
"""
公告管理序列化器（由低代码生成器生成）
"""
from apps.system.models import Notice
from utils.web.serializers import CoreModelSerializer


class NoticeSerializer(CoreModelSerializer):
    class Meta(CoreModelSerializer.Meta):
        model = Notice
        fields = '__all__'
