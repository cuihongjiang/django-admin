# -*- coding: utf-8 -*-
"""
公告管理模型（由低代码生成器生成）

managed = False：数据表由生成器通过 schema_editor 直接创建，
不参与 makemigrations / migrate，避免与手写迁移产生冲突。
"""
from django.db import models

from utils.db.models import CoreModel


class Notice(CoreModel):

    title = models.CharField(max_length=255, verbose_name="标题", help_text="标题", null=True, blank=True)


    content = models.TextField(verbose_name="内容", help_text="内容", null=True, blank=True)


    status = models.BooleanField(default=False, verbose_name="状态", help_text="状态")


    class Meta:
        db_table = "system_notice"
        managed = False
        verbose_name = "公告管理"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
