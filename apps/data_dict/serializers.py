# -*- coding: utf-8 -*-
"""
数据字典域序列化器：字典 / 字典项 / 分类字典
"""
from apps.data_dict.models import CategoryDict, Dict, DictItem
from utils.web.serializers import CoreModelSerializer


class DictSerializer(CoreModelSerializer):
    class Meta(CoreModelSerializer.Meta):
        model = Dict
        fields = '__all__'


class DictItemSerializer(CoreModelSerializer):
    class Meta(CoreModelSerializer.Meta):
        model = DictItem
        fields = '__all__'


class CategoryDictSerializer(CoreModelSerializer):
    class Meta(CoreModelSerializer.Meta):
        model = CategoryDict
        fields = '__all__'


__all__ = ["DictSerializer", "DictItemSerializer", "CategoryDictSerializer"]
