# -*- coding: utf-8 -*-
"""
代码生成模板引擎

基于 Jinja2，使用自定义定界符以避开生成代码中的冲突：
- 变量：[[ variable ]]
- 标签：[% if x %] ... [% endif %]
- 注释：[# 注释 #]

关闭 autoescape，保证生成的 Python/JS 代码原样输出。
"""
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent / "templates"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    variable_start_string="[[",
    variable_end_string="]]",
    block_start_string="[%",
    block_end_string="%]",
    comment_start_string="[#",
    comment_end_string="#]",
    autoescape=False,
    keep_trailing_newline=True,
    trim_blocks=False,
)


def _pylist(value) -> str:
    """渲染为 Python 列表字面量，用于生成代码中的字段清单"""
    return repr(list(value))


env.filters["pylist"] = _pylist


def render_template(template_name: str, context: dict) -> str:
    """按名称渲染 utils/generator/templates 下的模板文件"""
    template = env.get_template(template_name)
    return template.render(**context)
