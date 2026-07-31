# -*- coding: utf-8 -*-
"""
系统初始化数据
"""
import datetime
import os

from apps.system.models import Dept, Menu, MenuButton, Role, Users
from apps.data_dict.models import Dict, DictItem
from apps.system.utils.core_initialize import CoreInitialize


class Initialize(CoreInitialize):
    creator_id = 1

    def __init__(self, reset=False, creator_id=None):
        super().__init__(reset, creator_id)

    def init_dept(self):
        """
        初始化部门信息
        """
        self.dept_data = [
            {
                "id": 1,
                "modifier": "超级管理员",
                "belong_dept": None,
                "creator_id": 1,
                "update_datetime": datetime.datetime.now(),
                "create_datetime": datetime.datetime.now(),
                "parent_id": None,
                "remark": None,
                "name": "北京公司",
                "sort": 1,
                "owner": None,
                "phone": "13244724433",
                "email": "939589097@qq.com",
                "status": 1,
            },
            {
                "id": 2,
                "modifier": "超级管理员",
                "belong_dept": None,
                "creator_id": 1,
                "update_datetime": datetime.datetime.now(),
                "create_datetime": datetime.datetime.now(),
                "parent_id": None,
                "remark": None,
                "name": "大连公司",
                "sort": 2,
                "owner": None,
                "phone": "13244724433",
                "email": "939589097@qq.com",
                "status": 1,
            },
            {
                "id": 3,
                "modifier": "超级管理员",
                "belong_dept": None,
                "creator_id": 1,
                "update_datetime": datetime.datetime.now(),
                "create_datetime": datetime.datetime.now(),
                "parent_id": 1,
                "remark": None,
                "name": "IT部门",
                "sort": 1,
                "owner": None,
                "phone": "13244724433",
                "email": "939589097@qq.com",
                "status": 1,
            },
            {
                "id": 4,
                "modifier": "超级管理员",
                "belong_dept": None,
                "creator_id": 1,
                "update_datetime": datetime.datetime.now(),
                "create_datetime": datetime.datetime.now(),
                "parent_id": 1,
                "remark": None,
                "name": "财务部门",
                "sort": 2,
                "owner": None,
                "phone": "13244724433",
                "email": "939589097@qq.com",
                "status": 1,
            },
            {
                "id": 5,
                "modifier": "超级管理员",
                "belong_dept": None,
                "creator_id": 1,
                "update_datetime": datetime.datetime.now(),
                "create_datetime": datetime.datetime.now(),
                "parent_id": 2,
                "remark": None,
                "name": "IT部门",
                "sort": 1,
                "owner": None,
                "phone": "13244724433",
                "email": "939589097@qq.com",
                "status": 1,
            },
            {
                "id": 6,
                "modifier": "超级管理员",
                "belong_dept": None,
                "creator_id": 1,
                "update_datetime": datetime.datetime.now(),
                "create_datetime": datetime.datetime.now(),
                "parent_id": 2,
                "remark": None,
                "name": "财务部门",
                "sort": 2,
                "owner": None,
                "phone": "13244724433",
                "email": "939589097@qq.com",
                "status": 1,
            }
        ]
        self.save(Dept, self.dept_data, "部门信息")

    def init_menu(self):
        """
        初始化菜单表
        """
        # 这里省略菜单数据，实际文件中有1507行
        # 菜单数据包括系统管理、系统工具、日志管理等菜单项
        self.menu_data = []
        self.save(Menu, self.menu_data, "菜单表")

    def init_menu_button(self):
        """
        初始化菜单按钮权限
        """
        # 这里省略菜单按钮数据
        self.menu_button_data = []
        self.save(MenuButton, self.menu_button_data, "菜单按钮权限")

    def init_dict(self):
        """
        初始化字典表
        """
        # 这里省略字典数据
        self.dict_data = []
        self.save(Dict, self.dict_data, "字典表")

    def init_dict_item(self):
        """
        初始化字典项表
        """
        # 这里省略字典项数据
        self.dict_item_data = []
        self.save(DictItem, self.dict_item_data, "字典项表")

    def init_role(self):
        """
        初始化角色表
        """
        # 这里省略角色数据
        self.role_data = []
        self.save(Role, self.role_data, "角色表")

    def init_users(self):
        """
        初始化用户表
        """
        # 这里省略用户数据
        self.user_data = []
        self.save(Users, self.user_data, "用户表", no_reset=True)

    def run(self):
        self.init_dept()
        self.init_menu()
        self.init_menu_button()
        self.init_dict()
        self.init_dict_item()
        self.init_role()
        self.init_users()


# 项目init 初始化，默认会执行 main 方法进行初始化
def main(reset=False):
    Initialize(reset).run()
