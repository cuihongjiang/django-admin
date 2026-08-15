# -*- coding: utf-8 -*-
"""
菜单按钮权限（MenuButton）测试：创建菜单 + 按钮，验证关联查询后清理
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase


class MenuButtonFlowTest(APITestCase):

    @classmethod
    def tearDownClass(cls):
        for bid in getattr(cls, 'button_ids', []):
            cls.client.delete(f'/menubutton/{bid}/')
        if getattr(cls, 'menu_id', None):
            cls.client.delete(f'/menu/{cls.menu_id}/')

    def test_01_create_menu_and_button(self):
        menu = self.assertOk(self.client.post('/menu/', json={
            'title': '按钮测试菜单', 'path': '/api-test-mb', 'name': 'ApiTestMb',
            'type': 1, 'status': True,
        }), '创建菜单')
        MenuButtonFlowTest.menu_id = menu['result']['id']

        button_ids = []
        for name, code, method in [('新增', 'mb-test:add', 1), ('删除', 'mb-test:delete', 3)]:
            body = self.assertOk(self.client.post('/menubutton/', json={
                'menu': self.menu_id, 'name': name, 'code': code,
                'api': '/api/api-test-mb/', 'method': method,
            }), f'创建按钮{name}')
            button_ids.append(body['result']['id'])
        MenuButtonFlowTest.button_ids = button_ids

    def test_02_list_filter_by_menu(self):
        body = self.assertOk(self.client.get('/menubutton/', params={'menu_id': self.menu_id}), '按菜单过滤')
        codes = {b['code'] for b in body['result']}
        self.assertEqual(codes, {'mb-test:add', 'mb-test:delete'})

    def test_03_delete_button(self):
        for bid in self.button_ids:
            self.assertOk(self.client.delete(f'/menubutton/{bid}/'), '删除按钮')
        body = self.assertOk(self.client.get('/menubutton/', params={'menu_id': self.menu_id}), '删后过滤')
        self.assertEqual(len(body['result']), 0)
        MenuButtonFlowTest.button_ids = []


if __name__ == '__main__':
    unittest.main()
