# -*- coding: utf-8 -*-
"""
[[ name ]]序列化器（由低代码生成器生成）
"""
from apps.[[ app_label ]].models import [[ model_name ]]
from utils.web.serializers import CoreModelSerializer


class [[ model_name ]]Serializer(CoreModelSerializer):
    class Meta(CoreModelSerializer.Meta):
        model = [[ model_name ]]
        fields = '__all__'
