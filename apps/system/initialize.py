# -*- coding: utf-8 -*-
"""
系统管理域初始化数据（部门 / 菜单 / 菜单按钮 / 权限标识 / 角色 / 用户兜底）

维护工作流：
- 页面上调整了菜单、按钮、部门、角色、字典后，执行 `python manage.py dump_init`
  重新生成 apps/system/initialize_data.py 与 apps/data_dict/initialize_data.py 并提交，
  保证 `python manage.py init -y` 重置后数据不回退
- initialize_data.py 由命令生成，请勿手工编辑；用户种子数据（含密码）例外，在本文件手工维护

id 约定：初始化数据使用固定 id，为避免与页面自增 id 冲突，
后续在 initialize_data 中新增的数据请使用 >= 1000 的 id 段。

- python manage.py init     幂等补齐缺失数据（按 id get_or_create，不更新已有行、不删除多余行）
- python manage.py init -y  重置模式：先清空再重建（用户表 no_reset 除外，不会动已有用户；
  注意：重置会清掉页面给用户配置的角色关联，仅恢复下方用户数据声明的关联）
"""
from apps.system.models import Button, Dept, Menu, MenuButton, Role, Users
from apps.system.initialize_data import (
    BUTTON_DATA, DEPT_DATA, MENU_BUTTON_DATA, MENU_DATA, ROLE_DATA,
)
from apps.system.utils.core_initialize import CoreInitialize


class Initialize(CoreInitialize):
    creator_id = 1

    def __init__(self, reset=False, creator_id=None):
        super().__init__(reset, creator_id)

    def init_dept(self):
        """
        初始化部门信息
        """
        self.save(Dept, DEPT_DATA, "部门信息")

    def init_menu(self):
        """
        初始化菜单表
        """
        self.save(Menu, MENU_DATA, "菜单表")

    def init_menu_button(self):
        """
        初始化菜单按钮权限
        """
        self.save(MenuButton, MENU_BUTTON_DATA, "菜单按钮权限")

    def init_button(self):
        """
        初始化权限标识表
        """
        self.save(Button, BUTTON_DATA, "权限标识表")

    def init_role(self):
        """
        初始化角色表
        """
        self.save(Role, ROLE_DATA, "角色表")

    def init_users(self):
        """
        初始化用户表（no_reset=True：重置模式下也不会清空已有用户）

        仅兜底超级管理员账号，初始密码 admin123，生产环境请务必修改
        """
        self.user_data = [
            {
                "id": 1,
                "username": "superadmin",
                "password": "pbkdf2_sha256$1200000$vmuV2cupONnrOIg2J0vmeR$P1BvwGVx8Xwnhms/EZU0eiwfMzR5xgQYQTfVcIq9N7M=",
                "name": "superadmin",
                "is_superuser": True,
                "is_staff": True,
                "is_active": True,
                "gender": 1,
                "user_type": 0,
                "status": True,
                "modifier": "超级管理员",
                "creator_id": 1,
                "sort": 1,
                "role": [2],
            },
        ]
        self.save(Users, self.user_data, "用户表", no_reset=True)

    def run(self):
        self.init_dept()
        self.init_menu()
        self.init_menu_button()
        self.init_button()
        self.init_role()
        self.init_users()


# 项目init 初始化，默认会执行 main 方法进行初始化
def main(reset=False):
    Initialize(reset).run()
