# -*- coding: utf-8 -*-
# @Time    : 2026/07/31 10:00
# @Author  : 崔宏江
# @FileName: serializers.py
# @Software: PyCharm
# -*- coding: utf-8 -*-
from rest_framework import serializers


class CoreModelSerializer(serializers.ModelSerializer):
    """
    标准化序列化器基类
    审计字段只读，由视图层自动填充（见 CoreModelViewSet.perform_create/perform_update）
    """
    creator_name = serializers.SlugRelatedField(
        source='creator', slug_field='username', read_only=True
    )

    class Meta:
        # 子类需指定 model；fields = '__all__' 时审计字段自动只读
        read_only_fields = ['creator', 'modifier', 'belong_dept',
                            'create_datetime', 'update_datetime']
