# -*- coding: utf-8 -*-
"""
由 `python manage.py dump_init` 生成，请勿手工编辑。

在页面上调整了数据字典域（字典/字典项）后，重新执行 dump_init 并提交本文件，
保证 `python manage.py init -y` 重置后数据不回退。
"""

DICT_DATA = [
    {
        "id": 1,
        "modifier": "超级管理员",
        "name": "项目状态",
        "code": "project_status",
        "status": True,
        "sort": 1,
    },
    {
        "id": 19,
        "modifier": "react-admin",
        "name": "数据权限范围",
        "code": "data_range",
        "status": True,
        "sort": 1,
    },
    {
        "id": 20,
        "modifier": "react-admin",
        "name": "菜单类型",
        "code": "menu_type",
        "status": True,
        "sort": 1,
    },
    {
        "id": 25,
        "modifier": "react-admin",
        "name": "岗位状态",
        "code": "post_status",
        "status": True,
        "sort": 1,
    },
]

DICT_ITEM_DATA = [
    {
        "id": 1,
        "modifier": "超级管理员",
        "dict_id": 1,
        "label": "未建",
        "value": "未建",
        "status": True,
        "sort": 2,
    },
    {
        "id": 2,
        "modifier": "超级管理员",
        "dict_id": 1,
        "label": "在建",
        "value": "在建",
        "status": True,
        "sort": 1,
    },
    {
        "id": 3,
        "modifier": "超级管理员",
        "dict_id": 1,
        "label": "竣工",
        "value": "竣工",
        "status": True,
        "sort": 3,
    },
    {
        "id": 12,
        "dict_id": 19,
        "label": "仅本人",
        "value": "0",
        "status": True,
        "sort": 1,
    },
    {
        "id": 13,
        "dict_id": 19,
        "label": "本部门",
        "value": "1",
        "status": True,
        "sort": 1,
    },
    {
        "id": 14,
        "dict_id": 19,
        "label": "本部门及以下",
        "value": "2",
        "status": True,
        "sort": 1,
    },
    {
        "id": 15,
        "dict_id": 19,
        "label": "全部数据",
        "value": "3",
        "status": True,
        "sort": 1,
    },
    {
        "id": 16,
        "dict_id": 19,
        "label": "自定数据",
        "value": "4",
        "status": True,
        "sort": 1,
    },
    {
        "id": 17,
        "dict_id": 20,
        "label": "目录",
        "value": "0",
        "status": True,
        "sort": 1,
    },
    {
        "id": 18,
        "dict_id": 20,
        "label": "菜单",
        "value": "1",
        "status": True,
        "sort": 1,
    },
    {
        "id": 21,
        "dict_id": 25,
        "label": "在职",
        "value": "1",
        "status": True,
        "sort": 1,
    },
    {
        "id": 22,
        "dict_id": 25,
        "label": "离职",
        "value": "0",
        "status": True,
        "sort": 1,
    },
]
