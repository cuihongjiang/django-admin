# -*- coding: utf-8 -*-
"""
代码生成器域模型：GeneratorTemplate
"""
from django.db import models

from utils.db.models import CoreModel


class GeneratorTemplate(CoreModel):
    name = models.CharField(null=False, max_length=64, verbose_name="模板名称", help_text="模板名称")
    code = models.CharField(max_length=32, verbose_name="模板编码", help_text="模板编码")
    app_label = models.CharField(max_length=64, verbose_name="所属应用", null=True, blank=True,
                                 help_text="所属应用，如 system")
    model_name = models.CharField(max_length=64, verbose_name="模型名称", null=True, blank=True,
                                  help_text="模型名称，如 Post")
    form_info = models.TextField(verbose_name="表单信息", help_text="表单信息")
    table_info = models.TextField(verbose_name="表格信息", help_text="表格信息")
    has_menu = models.BooleanField(default=False, verbose_name="是否已经生成菜单", help_text="是否已经生成菜单")

    class Meta:
        db_table = "system_generator_template"
        verbose_name = '代码生成器模板'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
