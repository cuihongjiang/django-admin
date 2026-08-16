# -*- coding: utf-8 -*-
"""
导出当前库的初始化数据，生成 initialize_data 数据模块：

python manage.py dump_init

生成/覆盖两个文件：
- apps/system/initialize_data.py     （部门 / 菜单 / 菜单按钮 / 权限标识 / 角色）
- apps/data_dict/initialize_data.py  （字典 / 字典项）

维护工作流：在页面上调整了菜单、按钮、部门、角色、字典后，执行本命令并提交生成的文件，
保证 `python manage.py init -y` 重置后数据不回退。
用户表不导出（密码敏感），超级管理员兜底数据在 apps/system/initialize.py 中手工维护。
"""
import os

from django.core.management.base import BaseCommand

from apps.data_dict.models import Dict, DictItem
from apps.system.models import Button, Dept, Menu, MenuButton, Role

# (模型, 导出变量名, 标量字段, 多对多字段)
SYSTEM_TARGETS = [
    (Dept, 'DEPT_DATA',
     ['id', 'creator_id', 'modifier', 'parent_id', 'name', 'owner', 'phone', 'email', 'status', 'sort'], []),
    (Menu, 'MENU_DATA',
     ['id', 'creator_id', 'modifier', 'parent_id', 'icon', 'title', 'permission', 'is_ext', 'type',
      'path', 'redirect', 'component', 'name', 'status', 'keepalive', 'hide_menu', 'sort'], []),
    (MenuButton, 'MENU_BUTTON_DATA',
     ['id', 'creator_id', 'modifier', 'menu_id', 'name', 'code', 'api', 'method', 'sort'], []),
    (Button, 'BUTTON_DATA',
     ['id', 'creator_id', 'modifier', 'name', 'code', 'status', 'sort'], []),
    (Role, 'ROLE_DATA',
     ['id', 'creator_id', 'modifier', 'name', 'code', 'status', 'admin', 'data_range', 'sort'],
     ['menu', 'permission', 'dept', 'column']),
]

DICT_TARGETS = [
    (Dict, 'DICT_DATA',
     ['id', 'creator_id', 'modifier', 'name', 'code', 'status', 'sort', 'remark'], []),
    (DictItem, 'DICT_ITEM_DATA',
     ['id', 'creator_id', 'modifier', 'dict_id', 'label', 'value', 'status', 'sort', 'icon'], []),
]

HEADER = '''# -*- coding: utf-8 -*-
"""
由 `python manage.py dump_init` 生成，请勿手工编辑。

在页面上调整了{domain}后，重新执行 dump_init 并提交本文件，
保证 `python manage.py init -y` 重置后数据不回退。
"""
'''


def fmt_value(value):
    if value is True:
        return 'True'
    if value is False:
        return 'False'
    if value is None:
        return 'None'
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        if '"' not in value and '\\' not in value and '\n' not in value:
            return f'"{value}"'
        return repr(value)
    raise TypeError(f'不支持的导出类型: {type(value)}')


def export_rows(queryset, scalar_fields, m2m_fields):
    rows = []
    for obj in queryset.order_by('id'):
        row = {}
        for field in scalar_fields:
            value = getattr(obj, field)
            if value is not None:
                row[field] = value
        for field in m2m_fields:
            ids = sorted(getattr(obj, field).values_list('id', flat=True))
            if ids:
                row[field] = ids
        rows.append(row)
    return rows


def render_module(header_domain, targets):
    lines = [HEADER.format(domain=header_domain)]
    counts = {}
    for model, var_name, scalar_fields, m2m_fields in targets:
        rows = export_rows(model.objects.all(), scalar_fields, m2m_fields)
        counts[var_name] = len(rows)
        lines.append(f'{var_name} = [')
        for row in rows:
            lines.append('    {')
            for key, value in row.items():
                lines.append(f'        "{key}": {fmt_value(value)},')
            lines.append('    },')
        lines.append(']')
        lines.append('')
    return '\n'.join(lines), counts


class Command(BaseCommand):
    help = '导出当前库的初始化数据，生成 initialize_data 数据模块'

    def handle(self, *args, **options):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        outputs = [
            (os.path.join(project_root, 'apps', 'system', 'initialize_data.py'),
             '系统管理域（部门/菜单/菜单按钮/权限标识/角色）', SYSTEM_TARGETS),
            (os.path.join(project_root, 'apps', 'data_dict', 'initialize_data.py'),
             '数据字典域（字典/字典项）', DICT_TARGETS),
        ]
        for path, domain, targets in outputs:
            content, counts = render_module(domain, targets)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.stdout.write(self.style.SUCCESS(
                f'已生成 {os.path.relpath(path, project_root)}：' +
                ', '.join(f'{k} {v} 条' for k, v in counts.items())))
        self.stdout.write('请将生成的文件一并提交，保证 init -y 重置后数据不回退。')
