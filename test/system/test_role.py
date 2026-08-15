# -*- coding: utf-8 -*-
"""
角色管理测试：CRUD（M2M 可缺省）+ 菜单/按钮/列权限查询
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase


class RoleFlowTest(APITestCase):

    code = 'api_test_role'

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'role_id', None):
            cls.client.delete(f'/role/{cls.role_id}/')

    def test_01_create_without_m2m(self):
        """不传 menu/dept/permission/column 也能创建角色"""
        body = self.assertOk(self.client.post('/role/', json={
            'name': '接口测试角色', 'code': self.code, 'status': True, 'data_range': 0,
        }), '创建角色')
        RoleFlowTest.role_id = body['result']['id']

    def test_02_list_menu(self):
        self.assertOk(self.client.get('/role/list/menu/'), '角色可选菜单')

    def test_03_list_menu_button(self):
        self.assertOk(self.client.get('/role/list/menu_button/'), '角色可选按钮')

    def test_04_list_menu_column(self):
        self.assertOk(self.client.get('/role/list/menu_column/'), '角色可选列')

    def test_05_update(self):
        body = self.assertOk(self.client.put(f'/role/{self.role_id}/', json={
            'name': '接口测试角色-改', 'code': self.code, 'status': True, 'data_range': 3,
        }), '更新角色')
        self.assertEqual(body['result']['name'], '接口测试角色-改')

    def test_06_detail(self):
        body = self.assertOk(self.client.get(f'/role/{self.role_id}/'), '角色详情')
        self.assertEqual(body['result']['code'], self.code)

    def test_07_delete(self):
        self.assertOk(self.client.delete(f'/role/{self.role_id}/'), '删除角色')
        RoleFlowTest.role_id = None


if __name__ == '__main__':
    unittest.main()
