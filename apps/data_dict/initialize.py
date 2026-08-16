# -*- coding: utf-8 -*-
"""
数据字典域初始化数据（字典 / 字典项）

数据由 `python manage.py dump_init` 生成到 apps/data_dict/initialize_data.py，请勿手工编辑；
页面上调整字典后，重新执行 dump_init 并提交。
"""
from apps.data_dict.initialize_data import DICT_DATA, DICT_ITEM_DATA
from apps.data_dict.models import Dict, DictItem
from apps.system.utils.core_initialize import CoreInitialize


class Initialize(CoreInitialize):
    creator_id = 1

    def __init__(self, reset=False, creator_id=None):
        super().__init__(reset, creator_id)

    def init_dict(self):
        """
        初始化字典表
        """
        self.save(Dict, DICT_DATA, "字典表")

    def init_dict_item(self):
        """
        初始化字典项表
        """
        self.save(DictItem, DICT_ITEM_DATA, "字典项表")

    def run(self):
        self.init_dict()
        self.init_dict_item()


# 项目init 初始化，默认会执行 main 方法进行初始化
def main(reset=False):
    Initialize(reset).run()
