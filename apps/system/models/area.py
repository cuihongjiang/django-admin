# -*- coding: utf-8 -*-
"""
地区域模型：Area（由 init_area 命令导入 pca-code 数据）
"""
from django.db import models

from utils.db.models import CoreModel


class Area(CoreModel):
    name = models.CharField(max_length=100, verbose_name="名称", help_text="名称")
    code = models.CharField(max_length=20, verbose_name="地区编码", help_text="地区编码", unique=True, db_index=True)
    level = models.BigIntegerField(verbose_name="地区层级(1省份 2城市 3区县 4乡级)",
                                   help_text="地区层级(1省份 2城市 3区县 4乡级)")
    pinyin = models.CharField(max_length=255, verbose_name="拼音", help_text="拼音")
    initials = models.CharField(max_length=20, verbose_name="首字母", help_text="首字母")
    enable = models.BooleanField(default=True, verbose_name="是否启用", help_text="是否启用")
    pcode = models.ForeignKey(to='self', verbose_name='父地区编码', to_field="code", on_delete=models.CASCADE,
                              db_constraint=False, null=True, blank=True, help_text="父地区编码")

    class Meta:
        db_table = "system_area"
        verbose_name = '地区表'
        verbose_name_plural = verbose_name
        ordering = ('code',)

    def __str__(self):
        return f"{self.name}"
