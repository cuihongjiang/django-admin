# -*- coding: utf-8 -*-
"""
数据字典域模型：字典 / 字典项 / 分类字典
"""
from django.db import models

from utils.db.models import CoreModel


class Dict(CoreModel):
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="字典名称", help_text="字典名称")
    code = models.CharField(max_length=100, blank=True, null=True, verbose_name="编码", help_text="编码")
    status = models.BooleanField(default=True, blank=True, verbose_name="状态", help_text="状态")
    remark = models.CharField(max_length=2000, blank=True, null=True, verbose_name="备注", help_text="备注")

    class Meta:
        db_table = 'system_dict'
        verbose_name = "字典表"
        verbose_name_plural = verbose_name
        ordering = ('sort',)


class DictItem(CoreModel):
    icon = models.CharField(max_length=100, blank=True, null=True, verbose_name="ICON", help_text="ICON")
    label = models.CharField(max_length=100, blank=True, null=True, verbose_name="显示名称", help_text="显示名称")
    value = models.CharField(max_length=100, blank=True, null=True, verbose_name="实际值", help_text="实际值")
    status = models.BooleanField(default=True, blank=True, verbose_name="状态", help_text="状态")
    dict = models.ForeignKey(to="Dict", db_constraint=False, related_name="dictItem", on_delete=models.CASCADE,
                             help_text="字典")
    remark = models.CharField(max_length=2000, blank=True, null=True, verbose_name="备注", help_text="备注")

    class Meta:
        db_table = 'system_dict_item'
        verbose_name = "字典表详情表"
        verbose_name_plural = verbose_name
        ordering = ('sort',)


class CategoryDict(CoreModel):
    label = models.CharField(max_length=100, blank=True, null=True, verbose_name="显示名称", help_text="显示名称")
    value = models.CharField(max_length=100, blank=True, null=True, verbose_name="实际值", help_text="实际值")
    code = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="编码", help_text="编码")
    parent = models.ForeignKey(to='CategoryDict', on_delete=models.CASCADE, default=None, verbose_name="上级",
                               db_constraint=False, null=True, blank=True, help_text="上级")

    class Meta:
        db_table = 'system_category_dict'
        verbose_name = "分类字典表"
        verbose_name_plural = verbose_name
        ordering = ('sort',)
