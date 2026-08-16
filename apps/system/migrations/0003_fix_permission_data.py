# -*- coding: utf-8 -*-
"""
权限相关存量数据修复（随 migrate 分发到各环境，幂等）：

1. 清理挂在已删除菜单（旧菜单管理/部门管理/角色管理，id 4/7/8）上的孤儿按钮权限
2. 修正 id=35（demo:update）的 method：DELETE -> PUT
3. 为用户管理菜单（id=68）补齐 user:* 按钮权限，api 对齐当前路由
4. data_range 语义修正：DataPermissionMixin 已对齐 Role.DATASCOPE_CHOICES
   （3=全部数据权限，4=自定数据权限），旧实现恰好 3/4 互换；
   为保持线上实际行为不变，将存量角色的 3/4 值互换
5. 清理永不过期的数据权限缓存 user_data_range:*
"""
import logging

from django.db import migrations

logger = logging.getLogger(__name__)

USER_BUTTONS = [
    (109, '查询', 'user:search', 0, '/api/user/'),
    (110, '新增', 'user:add', 1, '/api/user/'),
    (111, '修改', 'user:update', 2, '/api/user/{id}'),
    (112, '删除', 'user:delete', 3, '/api/user/{id}'),
]


def fix_data(apps, schema_editor):
    Menu = apps.get_model('system', 'Menu')
    MenuButton = apps.get_model('system', 'MenuButton')
    Role = apps.get_model('system', 'Role')

    # 1. 孤儿按钮清理：先于新增执行，避免误删本次补建的按钮
    menu_ids = set(Menu.objects.values_list('id', flat=True))
    orphan_qs = MenuButton.objects.exclude(menu_id__in=menu_ids)
    orphan_count = orphan_qs.count()
    if orphan_count:
        orphan_qs.delete()
        logger.info('已清理孤儿菜单按钮 %s 条', orphan_count)

    # 2. id=35 method 修正（仅当仍为错误值时更新）
    MenuButton.objects.filter(id=35, method=3).update(method=2)

    # 3. 用户管理菜单补齐 user:* 按钮
    for button_id, name, code, method, api in USER_BUTTONS:
        MenuButton.objects.get_or_create(
            id=button_id,
            defaults={
                'menu_id': 68,
                'name': name,
                'code': code,
                'method': method,
                'api': api,
                'sort': button_id,
                'creator_id': 1,
                'modifier': '超级管理员',
            },
        )

    # 4. data_range 3/4 互换（先取 id 集合再更新，避免二次覆盖）
    ids_of_3 = list(Role.objects.filter(data_range=3).values_list('id', flat=True))
    ids_of_4 = list(Role.objects.filter(data_range=4).values_list('id', flat=True))
    Role.objects.filter(id__in=ids_of_3).update(data_range=4)
    Role.objects.filter(id__in=ids_of_4).update(data_range=3)
    if ids_of_3 or ids_of_4:
        logger.info('data_range 3/4 互换完成：3->4 %s 个角色，4->3 %s 个角色',
                    len(ids_of_3), len(ids_of_4))

    # 5. 数据权限缓存永不过期（TIMEOUT=None），必须显式清理
    try:
        from django.core.cache import cache
        cache.delete_pattern('user_data_range:*')
    except Exception:
        logger.warning('清理 user_data_range 缓存失败，请手动清理或等待缓存失效', exc_info=True)


def rollback(apps, schema_editor):
    # 数据修复迁移不回滚数据（回滚 schema 时保留现值即可）
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0002_generatortemplate_app_label_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_data, rollback),
    ]
