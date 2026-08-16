# -*- coding: utf-8 -*-
"""
数据一致性校验：检测悬空引用（模型普遍 db_constraint=False，数据库层面不拦截）

python manage.py check_data_integrity          仅检测并报告
python manage.py check_data_integrity --fix    检测并清理悬空数据（孤儿按钮/列权限行、多对多悬空关联）

覆盖范围：
- 菜单按钮 / 菜单列权限 挂在已不存在的菜单上
- 菜单 / 部门 的上级引用缺失
- 角色-菜单/按钮/部门/列、用户-角色/岗位 的多对多关联指向已不存在的行
- 用户所属部门缺失
"""
from django.core.management.base import BaseCommand

from apps.data_dict.models import Dict, DictItem
from apps.system.models import (
    Button, Dept, Menu, MenuButton, MenuColumnField, Post, Role, Users,
)


class Command(BaseCommand):
    help = '数据一致性校验：检测（并可清理）db_constraint=False 导致的悬空引用'

    def add_arguments(self, parser):
        parser.add_argument('--fix', action='store_true', help='清理检测到的悬空数据')

    def handle(self, *args, **options):
        fix = options['fix']
        problems = 0

        def report(name, qs, sample_field='id'):
            nonlocal problems
            count = qs.count()
            if not count:
                return
            problems += count
            sample = list(qs.values_list(sample_field, flat=True)[:10])
            self.stdout.write(self.style.WARNING(f'  [{name}] {count} 条，示例 {sample}'))

        self.stdout.write('数据一致性校验：')

        # ---- 挂在已删除菜单上的按钮 / 列权限 ----
        menu_ids = set(Menu.objects.values_list('id', flat=True))
        orphan_buttons = MenuButton.objects.exclude(menu_id__in=menu_ids)
        orphan_columns = MenuColumnField.objects.exclude(menu_id__in=menu_ids)
        report('孤儿菜单按钮(menu_id悬空)', orphan_buttons)
        report('孤儿菜单列权限(menu_id悬空)', orphan_columns)

        # ---- 上级引用悬空 ----
        report('菜单上级悬空(parent_id)',
               Menu.objects.exclude(parent_id__isnull=True).exclude(parent_id__in=menu_ids), 'parent_id')
        dept_ids = set(Dept.objects.values_list('id', flat=True))
        report('部门上级悬空(parent_id)',
               Dept.objects.exclude(parent_id__isnull=True).exclude(parent_id__in=dept_ids), 'parent_id')

        # ---- 多对多关联悬空（关联表无库级约束，目标被物理删除后关联残留） ----
        def check_m2m(name, model, field_name, valid_ids):
            m2m_field = model._meta.get_field(field_name)
            through = m2m_field.remote_field.through
            # 关联表上指向目标模型的外键（关联列名与字段名可能不一致，如 permission -> menubutton_id）
            target_fk = next(
                f for f in through._meta.get_fields()
                if f.is_relation and not f.auto_created and f.related_model is m2m_field.related_model
            )
            orphan = through.objects.exclude(**{f'{target_fk.name}_id': None}).exclude(
                **{f'{target_fk.name}_id__in': valid_ids})
            report(name, orphan, 'id')
            return orphan

        role_menu = check_m2m('角色-菜单关联悬空', Role, 'menu', menu_ids)
        role_permission = check_m2m('角色-按钮关联悬空', Role, 'permission',
                                    set(MenuButton.objects.values_list('id', flat=True)))
        role_dept = check_m2m('角色-部门关联悬空', Role, 'dept', dept_ids)
        role_column = check_m2m('角色-列权限关联悬空', Role, 'column',
                                set(MenuColumnField.objects.values_list('id', flat=True)))
        user_role = check_m2m('用户-角色关联悬空', Users, 'role', set(Role.objects.values_list('id', flat=True)))
        user_post = check_m2m('用户-岗位关联悬空', Users, 'post', set(Post.objects.values_list('id', flat=True)))

        # ---- 外键悬空 ----
        report('用户所属部门悬空(dept_id)',
               Users.objects.exclude(dept_id__isnull=True).exclude(dept_id__in=dept_ids), 'dept_id')
        report('字典项所属字典悬空(dict_id)',
               DictItem.objects.exclude(dict_id__in=set(
                   Dict.objects.values_list('id', flat=True))), 'dict_id')

        if problems == 0:
            self.stdout.write(self.style.SUCCESS('  未发现悬空引用，数据一致性正常。'))
            return

        if not fix:
            self.stdout.write(self.style.WARNING(f'共发现 {problems} 条悬空引用。执行 --fix 可清理。'))
            return

        # --fix：仅清理悬空的按钮/列权限行与多对多残留关联，不删除任何主表数据
        deleted_buttons, _ = orphan_buttons.delete()
        deleted_columns, _ = orphan_columns.delete()
        deleted_links = sum(qs.delete()[0] for qs in
                            [role_menu, role_permission, role_dept, role_column, user_role, user_post])
        self.stdout.write(self.style.SUCCESS(
            f'已清理：孤儿按钮 {deleted_buttons} 条，孤儿列权限 {deleted_columns} 条，悬空多对多关联 {deleted_links} 条。'))
        self.stdout.write(self.style.WARNING('注意：上级悬空/部门悬空等主表引用未自动处理，请人工核对。'))
