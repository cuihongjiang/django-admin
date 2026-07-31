# -*- coding: utf-8 -*-
"""
文件管理域序列化器：File
"""
from apps.file.models import File
from utils.web.serializers import CoreModelSerializer


class FileSerializer(CoreModelSerializer):
    class Meta(CoreModelSerializer.Meta):
        model = File
        fields = '__all__'
        # 上传时由视图计算 md5/大小/存储名，不接受客户端提交
        read_only_fields = CoreModelSerializer.Meta.read_only_fields + [
            'save_name', 'size', 'md5sum'
        ]


__all__ = ["FileSerializer"]
