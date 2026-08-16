# -*- coding: utf-8 -*-
"""
[[ name ]]模型（由低代码生成器生成）

managed = False：数据表由生成器通过 schema_editor 直接创建，
不参与 makemigrations / migrate，避免与手写迁移产生冲突。
"""
from django.db import models

from utils.db.models import CoreModel


class [[ Camel ]](CoreModel):
[% for f in model_fields %]
    [[ f.field ]] = [[ f.decl ]]

[% endfor %]
    class Meta:
        db_table = "[[ db_table ]]"
        managed = False
        verbose_name = "[[ name ]]"
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)
