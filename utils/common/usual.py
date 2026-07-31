# -*- coding: utf-8 -*-
# @Time    : 2024/12/7 00:24
# @Author  : 崔宏江
# @FileName: usual.py
# @Software: PyCharm
"""
通用工具函数
"""


def insert_content_after_line(filename, target_line, content_to_insert):
    """在文件指定行后插入内容"""
    try:
        # 打开文件并读取内容
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # 找到目标行的索引位置
        target_line_index = None
        for i, line in enumerate(lines):
            if target_line in line:
                target_line_index = i
                break

        if target_line_index is not None:
            # 在目标行后面插入内容
            lines.insert(target_line_index + 1, content_to_insert + '\n')

            # 将更新后的内容写回文件中
            with open(filename, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            print("内容已成功插入到目标行后。")
        else:
            print("未找到目标行。")

    except FileNotFoundError:
        print(f"文件 '{filename}' 未找到。")
