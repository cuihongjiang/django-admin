# -*- coding: utf-8 -*-
"""
后端落地器：把生成配置物化为真实的数据表 + 可用接口（无需人工 copy）

幂等策略（每一步先查存在，存在即复用，缺失才创建）：
- 数据表     连接内省 table_names → schema_editor.create_model
- 模型文件   apps/system/models/{code}.py 已含 class {Camel}(CoreModel) 则复用
- 序列化器   apps/system/serializers/__init__.py 已含 class {Camel}Serializer 则跳过
- 视图集     apps/system/apis/{code}.py 已含 class {Camel}ViewSet 则复用
- 路由       apps/router.py 已注册 basename='{code}' 则跳过

已有模型的模板（is_new_table=False）不写任何文件，仅确认模型与路由存在。
文件写入后开发服务器（runserver）自动重载生效，生产环境需重启。
"""
import importlib
import re

from django.apps import apps
from django.db import connection

from manageSys.settings import BASE_DIR
from utils.generator.builder import build_context
from utils.generator.engine import render_template

CODE_PATTERN = re.compile(r'^[a-z][a-z0-9_]{1,30}$')


def _write_if_absent(path, content) -> str:
    """文件不存在则写入，返回 created / exists"""
    if path.exists():
        return 'exists'
    path.write_text(content, encoding='utf-8')
    return 'created'


def _append_if_absent(path, snippet, marker) -> str:
    """文件已含 marker 则跳过，否则追加 snippet，返回 created / exists"""
    text = path.read_text(encoding='utf-8')
    if marker in text:
        return 'exists'
    path.write_text(text.rstrip() + '\n\n' + snippet, encoding='utf-8')
    return 'created'


def materialize_backend(template) -> dict:
    """
    落地后端，返回各资源状态报告：
    {资源: 'created' | 'exists' | 'skipped'}，冲突时抛 ValueError
    """
    if not CODE_PATTERN.match(template.code or ''):
        raise ValueError('模板编码须为小写字母开头的标识符（字母/数字/下划线）')

    ctx = build_context(template)
    code = ctx['code']
    camel = ctx['Camel']

    # ---- 已有模型：表和代码天然存在，仅确认路由已注册 ----
    if not ctx['is_new_table']:
        try:
            apps.get_model(ctx['app_label'], ctx['model_name'])
        except LookupError:
            raise ValueError(
                f"模型 {ctx['app_label']}.{ctx['model_name']} 不存在，"
                f"请改用「新建数据表」模式或重新选择数据表"
            )
        router_py = BASE_DIR / 'apps' / 'router.py'
        routed = f"basename='{code}'" in router_py.read_text(encoding='utf-8')
        return {
            'table': 'exists',
            'model': 'exists',
            'serializer': 'exists' if routed else 'skipped',
            'viewset': 'exists' if routed else 'skipped',
            'router': 'exists' if routed else 'skipped',
        }

    if not ctx['form_fields']:
        raise ValueError('新建数据表至少需要配置一个表单字段（字段即表列）')

    report = {}

    # ---- 1. 模型文件（冲突检测：同名文件必须含同名类才视为生成物） ----
    models_dir = BASE_DIR / 'apps' / 'system' / 'models'
    model_file = models_dir / f'{code}.py'
    if model_file.exists():
        if f'class {camel}(CoreModel)' not in model_file.read_text(encoding='utf-8'):
            raise ValueError(f'models/{code}.py 已被其他模型占用，请更换模板编码')
        report['model'] = 'exists'
    else:
        report['model'] = _write_if_absent(model_file, render_template('drf_model.tpl', ctx))

    # 模型导出（models/__init__.py 追加 import）
    report['model_export'] = _append_if_absent(
        models_dir / '__init__.py',
        f'from apps.system.models.{code} import {camel}',
        f'from apps.system.models.{code} import',
    )

    # ---- 2. 数据表（schema_editor 直接建，managed=False 不走迁移） ----
    module = importlib.import_module(f'apps.system.models.{code}')
    model_cls = getattr(module, camel)
    table_names = connection.introspection.table_names()
    if model_cls._meta.db_table in table_names:
        report['table'] = 'exists'
    else:
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(model_cls)
        report['table'] = 'created'

    # ---- 3. 序列化器（追加到 serializers/__init__.py） ----
    ser_init = BASE_DIR / 'apps' / 'system' / 'serializers' / '__init__.py'
    if f'class {camel}Serializer' in ser_init.read_text(encoding='utf-8'):
        report['serializer'] = 'exists'
    else:
        ser_init.write_text(
            ser_init.read_text(encoding='utf-8').rstrip()
            + '\n\n\n' + render_template('drf_serializer.tpl', ctx),
            encoding='utf-8',
        )
        report['serializer'] = 'created'

    # ---- 4. 视图集文件 ----
    api_file = BASE_DIR / 'apps' / 'system' / 'apis' / f'{code}.py'
    if api_file.exists():
        if f'class {camel}ViewSet' not in api_file.read_text(encoding='utf-8'):
            raise ValueError(f'apis/{code}.py 已被其他视图集占用，请更换模板编码')
        report['viewset'] = 'exists'
    else:
        report['viewset'] = _write_if_absent(api_file, render_template('drf_viewset.tpl', ctx))

    # ---- 5. 路由注册（apps/router.py 追加 import + register） ----
    report['router'] = _append_if_absent(
        BASE_DIR / 'apps' / 'router.py',
        render_template('drf_router.tpl', ctx),
        f"basename='{code}'",
    )

    return report
