# -*- coding: utf-8 -*-
"""
代码生成构建器：解析模板配置 → 组装上下文 → 渲染文件 → zip 打包

支持两种前端技术栈（frontend 参数）：
- vue  : naive-ui-admin 风格页面 + api.js
- react: react-admin 模块契约（index.ts + api.ts + pages/XxxPage.tsx）
"""
import io
import json
import zipfile

from utils.generator.engine import render_template

# Vue 输出：(模板文件, 输出路径模板)
VUE_FILE_MAPPING = [
    ("vue_index.tpl", "frontend/[[code]]/index.vue"),
    ("vue_api.tpl", "frontend/[[code]]/api.js"),
    ("drf_serializer.tpl", "backend/serializer_[[code]].py"),
    ("drf_viewset.tpl", "backend/viewset_[[code]].py"),
    ("drf_router.tpl", "backend/router_snippet_[[code]].txt"),
]

# React 输出：模块契约目录结构
REACT_FILE_MAPPING = [
    ("react_index.tpl", "frontend/[[code]]/index.ts"),
    ("react_api.tpl", "frontend/[[code]]/api.ts"),
    ("react_page.tpl", "frontend/[[code]]/pages/[[camel]]Page.tsx"),
    ("drf_serializer.tpl", "backend/serializer_[[code]].py"),
    ("drf_viewset.tpl", "backend/viewset_[[code]].py"),
    ("drf_router.tpl", "backend/router_snippet_[[code]].txt"),
]


def to_camel(text: str) -> str:
    """kebab/snake case 转 PascalCase：'post-info' / 'post_info' -> 'PostInfo'"""
    return ''.join(part.capitalize() for part in text.replace('-', '_').split('_') if part)


def _parse_json_field(raw) -> list:
    """TextField 中存的 JSON 数据，兼容 str（存于 DB）和 list（来自 request.data）"""
    if isinstance(raw, list):
        return raw
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except (TypeError, ValueError):
        return []


def validate_config(table_info, form_info) -> None:
    """创建/更新模板时校验配置结构，抛 ValueError"""
    for label, raw in (('table_info', table_info), ('form_info', form_info)):
        data = _parse_json_field(raw)
        is_empty = (not raw) or (isinstance(raw, str) and not raw.strip())
        if not is_empty and not data:
            raise ValueError(f"{label} 必须是 JSON 数组")
        for item in data:
            if not isinstance(item, dict) or not item.get('field') or not item.get('title'):
                raise ValueError(f"{label} 中每个字段需包含 field 和 title")


def _derive_field(f: dict) -> dict:
    """为单个表单字段补充 React 模板所需的类型/校验/默认值属性"""
    f = dict(f)
    component = f.get('component') or 'input'
    required = bool(f.get('required'))
    title = f.get('title', f.get('field'))

    if component == 'switch':
        f['ts_type'] = 'boolean'
        f['zod_rule'] = 'z.boolean()'
        f['default_value'] = 'false'
    elif component == 'number':
        f['ts_type'] = 'number'
        f['zod_rule'] = (
            f"z.coerce.number({{ message: '请输入{title}' }})"
            if required else 'z.coerce.number().optional()'
        )
        f['default_value'] = '0'
    elif component == 'select':
        f['ts_type'] = 'string'
        f['zod_rule'] = f"z.string().min(1, '请选择{title}')" if required else 'z.string().optional()'
        f['default_value'] = "''"
    else:
        f['ts_type'] = 'string'
        f['zod_rule'] = f"z.string().min(1, '请输入{title}')" if required else 'z.string().optional()'
        f['default_value'] = "''"
    return f


def _model_decl(f: dict) -> str:
    """表单字段 → Django 模型字段声明代码（用于新建数据表）"""
    title = str(f.get('title') or f.get('field') or '').replace('"', '\\"')
    common = f'verbose_name="{title}", help_text="{title}", null=True, blank=True'
    component = f.get('component') or 'input'
    if component == 'textarea':
        return f'models.TextField({common})'
    if component == 'number':
        return f'models.IntegerField(default=0, {common})'
    if component == 'select':
        return f'models.CharField(max_length=64, {common})'
    if component == 'switch':
        return f'models.BooleanField(default=False, verbose_name="{title}", help_text="{title}")'
    return f'models.CharField(max_length=255, {common})'


def build_context(template) -> dict:
    """
    将 GeneratorTemplate 的配置转换为各模板渲染上下文

    table_info: [{field, title, is_search, is_list, width, component?, dict_code?}]
    form_info:  [{field, title, component(input/select/switch/number/textarea), required, dict_code}]
    """
    table_info = _parse_json_field(template.table_info)
    form_info = [_derive_field(f) for f in _parse_json_field(template.form_info)]

    required_fields = [f for f in form_info if f.get('required')]
    # 表单里 select 控件引用的字典编码（去重，保持顺序）
    dict_codes = list(dict.fromkeys(
        f['dict_code'] for f in form_info
        if f.get('component') == 'select' and f.get('dict_code')
    ))

    code = template.code or 'demo'
    camel = to_camel(code)
    form_defaults = '{' + ', '.join(
        f"{f['field']}: {f['default_value']}" for f in form_info
    ) + '}'
    # 列表列类型优先取同名表单字段的推导结果（switch→boolean 等），否则 string
    form_ts = {f['field']: f['ts_type'] for f in form_info}

    def _col(c: dict) -> dict:
        c = dict(c, ts_type=form_ts.get(c['field'], 'string'))
        # 列渲染 dict label 需要 component/dict_code 信息
        matched = next((f for f in form_info if f['field'] == c['field']), None)
        if matched and not c.get('component'):
            c['component'] = matched.get('component')
            c['dict_code'] = c.get('dict_code') or matched.get('dict_code')
        return c

    search_columns = [_col(c) for c in table_info if c.get('is_search')]
    list_columns = [_col(c) for c in table_info if c.get('is_list')]

    # 实体接口字段 = 列表列 ∪ 表单字段（按字段名去重，类型优先取表单推导）
    entity_fields, seen = [], set()
    for f in [*list_columns, *form_info]:
        if f['field'] not in seen:
            seen.add(f['field'])
            entity_fields.append({'field': f['field'], 'ts_type': f.get('ts_type', 'string')})

    context = {
        'code': code,
        'name': template.name or code,
        'app_label': template.app_label or 'system',
        'model_name': template.model_name or camel,
        'camel': camel,
        # 模板中 PascalCase 类型名使用（与 camel 同值，键名区分大小写）
        'Camel': camel,
        'is_new_table': bool(getattr(template, 'is_new_table', False)),
        'search_columns': search_columns,
        'entity_fields': entity_fields,
        'list_columns': list_columns,
        'form_fields': form_info,
        'required_fields': required_fields,
        'dict_codes': dict_codes,
        'has_select': any(f.get('component') == 'select' for f in form_info),
        'has_switch': any(f.get('component') == 'switch' for f in form_info),
        'has_input': any(f.get('component') != 'select' and f.get('component') != 'switch'
                         for f in form_info),
        'form_defaults': form_defaults,
        # 新建数据表模式：模型文件模板所需的建表信息
        'db_table': f'system_{code}',
        'model_fields': [
            {'field': f['field'], 'decl': _model_decl(f)} for f in form_info
        ],
        # Excel 导入导出字段 = 表格展示列；精确过滤字段 = 参与搜索的列
        'export_fields': [c['field'] for c in list_columns],
        'search_fields': [c['field'] for c in search_columns],
    }
    return context


def generate_files(template, frontend: str = 'vue') -> list:
    """渲染全部文件，返回 [{path, content}]；frontend 取 'vue' 或 'react'"""
    mapping = list(REACT_FILE_MAPPING if frontend == 'react' else VUE_FILE_MAPPING)
    context = build_context(template)
    # 新建数据表模式额外产出模型文件（放在后端文件首位）
    if context['is_new_table']:
        mapping.insert(3, ('drf_model.tpl', 'backend/model_[[code]].py'))
    files = []
    for tpl_name, out_path in mapping:
        content = render_template(tpl_name, context)
        out = (out_path
               .replace('[[code]]', context['code'])
               .replace('[[camel]]', context['camel']))
        files.append({'path': out, 'content': content})
    return files


def generate_zip(template, frontend: str = 'vue') -> bytes:
    """渲染全部文件并打包为 zip 字节流"""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in generate_files(template, frontend):
            zf.writestr(file['path'], file['content'])
    return buffer.getvalue()
