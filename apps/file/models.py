# -*- coding: utf-8 -*-
"""
文件管理域模型：File
"""
import os

from django.db import models

from utils.db.models import CoreModel


def media_file_name(instance, filename):
    h = instance.md5sum
    basename, ext = os.path.splitext(filename)
    return os.path.join('files', h[0:1], h[1:2], h + ext.lower())


class File(CoreModel):
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="实际名称", help_text="实际名称")
    save_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="存储名称", help_text="存储名称")
    url = models.FileField(upload_to=media_file_name, max_length=255, verbose_name="文件地址", help_text="文件地址")
    size = models.BigIntegerField(null=True, blank=True, verbose_name="大小", help_text="大小")
    md5sum = models.CharField(max_length=36, blank=True, verbose_name="文件md5", help_text="文件md5")

    class Meta:
        db_table = 'system_file'
        verbose_name = '文件管理'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
