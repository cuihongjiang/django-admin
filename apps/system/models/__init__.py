# -*- coding: utf-8 -*-
"""
系统管理域模型包：按业务域拆分为多个模块，此处统一汇总导出，
保证 `from apps.system.models import X` 的用法。
"""
from apps.system.models.system import (
    Users,
    Post,
    Role,
    Dept,
    Button,
    Menu,
    MenuButton,
    MenuColumnField,
)
from apps.system.models.area import Area
from apps.system.models.config import ApiWhiteList, SystemConfig
from apps.system.models.generator import GeneratorTemplate

__all__ = [
    "Users",
    "Post",
    "Role",
    "Dept",
    "Button",
    "Menu",
    "MenuButton",
    "MenuColumnField",
    "Area",
    "ApiWhiteList",
    "SystemConfig",
    "GeneratorTemplate",
]

from apps.system.models.notice import Notice