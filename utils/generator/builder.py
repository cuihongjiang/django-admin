# -*- coding: utf-8 -*-
"""
代码生成构建器：解析模板配置 → 组装上下文 → 渲染文件 → zip 打包
"""
import io
import json
import zipfile
from pathlib import Path

from utils.generator.engine import render_template

# 渲染输出的文件清单：(模板文件, 输出路径模板)
FILE_MAPPING = [
    ("vue_index.tpl", "frontend/[[code]]/index.vue"),
    ("vue_api.tpl", "frontend/[[code]]/api.js"),
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


def build_context(template) -> dict:
    """
    将 GeneratorTemplate 的配置转换为各模板渲染上下文

    table_info: [{field, title, is_search, is_list, width}]
    form_info:  [{field, title, component, required, dict_code}]
    """
    table_info = _parse_json_field(template.table_info)
    form_info = _parse_json_field(template.form_info)

    search_columns = [c for c in table_info if c.get('is_search')]
    list_columns = [c for c in table_info if c.get('is_list')]
    required_fields = [f for f in form_info if f.get('required')]
    # 表单里 select 控件引用的字典编码（去重，保持顺序）
    dict_codes = list(dict.fromkeys(
        f['dict_code'] for f in form_info
        if f.get('component') == 'select' and f.get('dict_code')
    ))

    code = template.code or 'demo'
    return {
        'code': code,
        'name': template.name or code,
        'app_label': template.app_label or 'system',
        'model_name': template.model_name or to_camel(code),
        'camel': to_camel(code),
        'search_columns': search_columns,
        'list_columns': list_columns,
        'form_fields': form_info,
        'required_fields': required_fields,
        'dict_codes': dict_codes,
        # Excel 导入导出字段 = 表格展示列；精确过滤字段 = 参与搜索的列
        'export_fields': [c['field'] for c in list_columns],
        'search_fields': [c['field'] for c in search_columns],
    }


def generate_files(template) -> list:
    """渲染全部文件，返回 [{path, content}]"""
    context = build_context(template)
    files = []
    for tpl_name, out_path in FILE_MAPPING:
        content = render_template(tpl_name, context)
        files.append({'path': out_path.replace('[[code]]', context['code']), 'content': content})
    return files


def generate_zip(template) -> bytes:
    """渲染全部文件并打包为 zip 字节流"""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in generate_files(template):
            zf.writestr(file['path'], file['content'])
    return buffer.getvalue()
