# -*- coding: utf-8 -*-
"""
数据修复与种子迁移（随 migrate 分发到各环境，幂等）：

1. belong_dept 回填：行级数据权限（DataPermissionMixin）按 belong_dept 过滤部门数据，
   历史数据该列基本为 NULL，按创建人当前所属部门回填；创建人缺失或创建人无部门的
   保持 NULL（视为无部门归属）
2. 接口白名单种子：/api/login/（与 settings.WHITE_LIST 初始值一致，method 留空放行全部方法）
3. 系统配置种子：DEMO / LOGIN_ANALYSIS_LOG 两个开关（对应 settings.DEMO 与
   settings.ENABLE_LOGIN_ANALYSIS_LOG，运行时经 get_system_config 表驱动读取）
"""
import logging

from django.db import migrations

logger = logging.getLogger(__name__)

# 所有带 belong_dept 审计列的业务表
BELONG_DEPT_TABLES = [
    'system_api_white_list',
    'system_area',
    'system_button',
    'system_category_dict',
    'system_config',
    'system_dept',
    'system_dict',
    'system_dict_item',
    'system_file',
    'system_generator_template',
    'system_login_log',
    'system_menu',
    'system_menu_button',
    'system_menu_column_field',
    'system_notice',
    'system_operation_log',
    'system_post',
    'system_role',
    'system_users',
]

CONFIG_SEEDS = [
    {'key': 'DEMO', 'title': '演示模式（只读放行）',
     'remark': '对应 settings.DEMO；开启后 GET/HEAD/OPTIONS 请求免认证', 'value': False},
    {'key': 'LOGIN_ANALYSIS_LOG', 'title': '登录日志IP详细解析',
     'remark': '对应 settings.ENABLE_LOGIN_ANALYSIS_LOG；开启后登录时调用外部接口解析IP归属地',
     'value': True},
]


def fix_data(apps, schema_editor):
    # 1. belong_dept 回填（跳过尚不存在的表：全新库按序 migrate 时部分表在本迁移之后才创建）
    existing_tables = set(schema_editor.connection.introspection.table_names())
    for table in BELONG_DEPT_TABLES:
        if table not in existing_tables:
            continue
        with schema_editor.connection.cursor() as cursor:
            # JOIN 派生表而非子查询：MySQL 不允许 UPDATE 目标表出现在 FROM 子查询中
            cursor.execute(f"""
                UPDATE `{table}` t
                JOIN (SELECT id, dept_id FROM system_users WHERE dept_id IS NOT NULL) u
                  ON u.id = t.creator_id
                SET t.belong_dept = u.dept_id
                WHERE t.belong_dept IS NULL AND t.creator_id IS NOT NULL
            """)
            if cursor.rowcount:
                logger.info('belong_dept 回填 %s：%s 行', table, cursor.rowcount)

    # 2. 接口白名单种子
    ApiWhiteList = apps.get_model('system', 'ApiWhiteList')
    ApiWhiteList.objects.get_or_create(
        url='/api/login/',
        defaults={'method': None, 'enable_datasource': False, 'creator_id': 1, 'modifier': '超级管理员'},
    )

    # 3. 系统配置种子
    SystemConfig = apps.get_model('system', 'SystemConfig')
    for seed in CONFIG_SEEDS:
        SystemConfig.objects.get_or_create(
            key=seed['key'],
            defaults={**seed, 'status': True, 'creator_id': 1, 'modifier': '超级管理员'},
        )

    # 4. 清理相关缓存（种子/回填后避免读到旧缓存）
    try:
        from django.core.cache import cache
        cache.delete_pattern('user_data_range:*')
        cache.delete_pattern('system_config:*')
        cache.delete('api_white_list')
    except Exception:
        logger.warning('清理缓存失败，可等待 TTL 过期', exc_info=True)


def rollback(apps, schema_editor):
    # 数据迁移不回滚
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0004_generatortemplate_has_backend_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_data, rollback),
    ]
