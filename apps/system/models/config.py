# -*- coding: utf-8 -*-
"""
系统配置域模型：接口白名单 / 系统配置
"""
from django.db import models

from utils.db.models import CoreModel


class ApiWhiteList(CoreModel):
    url = models.CharField(max_length=200, help_text="url地址", verbose_name="url")
    METHOD_CHOICES = (
        (0, "GET"),
        (1, "POST"),
        (2, "PUT"),
        (3, "DELETE"),
    )
    # method 留空（None）放行全部方法，配置了则仅放行对应方法
    method = models.IntegerField(default=None, verbose_name="接口请求方法", null=True, blank=True,
                                 help_text="接口请求方法")
    enable_datasource = models.BooleanField(default=True, verbose_name="激活数据权限", help_text="激活数据权限",
                                            blank=True)

    class Meta:
        db_table = "system_api_white_list"
        verbose_name = '接口白名单'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)


class SystemConfig(CoreModel):
    parent = models.ForeignKey(to='self', verbose_name='父级', on_delete=models.CASCADE,
                               db_constraint=False, null=True, blank=True, help_text="父级")
    title = models.CharField(max_length=50, verbose_name="标题", help_text="标题")
    key = models.CharField(max_length=20, verbose_name="键", help_text="键")
    # value 为 JSON 值；JSONField 不支持长度限制（MySQL 列为 json 类型），勿加 max_length
    value = models.JSONField(verbose_name="值", help_text="值", null=True, blank=True)
    status = models.BooleanField(default=False, verbose_name="启用状态", help_text="启用状态")
    data_options = models.JSONField(verbose_name="数据options", help_text="数据options", null=True, blank=True)
    FORM_ITEM_TYPE_LIST = (
        (0, 'text'),
        (1, 'textarea'),
        (2, 'number'),
        (3, 'select'),
        (4, 'radio'),
        (5, 'checkbox'),
        (6, 'date'),
        (7, 'datetime'),
        (8, 'time'),
        (9, 'imgs'),
        (10, 'files'),
        (11, 'array'),
        (12, 'foreignkey'),
        (13, 'manytomany'),
    )
    form_item_type = models.IntegerField(choices=FORM_ITEM_TYPE_LIST, verbose_name="表单类型", help_text="表单类型",
                                         default=0,
                                         blank=True)
    rule = models.JSONField(null=True, blank=True, verbose_name="校验规则", help_text="校验规则")
    placeholder = models.CharField(max_length=50, null=True, blank=True, verbose_name="提示信息", help_text="提示信息")
    setting = models.JSONField(null=True, blank=True, verbose_name="配置", help_text="配置")

    class Meta:
        db_table = "system_config"
        verbose_name = '系统配置表'
        verbose_name_plural = verbose_name
        ordering = ('sort',)

    def __str__(self):
        return f"{self.title}"
