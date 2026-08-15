# -*- coding: utf-8 -*-
"""
菜单管理测试：CRUD + 路由树
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase


class MenuFlowTest(APITestCase):

    path = '/api-test-menu'

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'menu_id', None):
            cls.client.delete(f'/menu/{cls.menu_id}/')

    def test_01_create(self):
        body = self.assertOk(self.client.post('/menu/', json={
            'title': '接口测试菜单', 'path': self.path, 'component': '/api-test/index',
            'name': 'ApiTest', 'type': 1, 'status': True,
        }), '创建菜单')
        MenuFlowTest.menu_id = body['result']['id']

    def test_02_list(self):
        body = self.assertOk(self.client.get('/menu/'), '菜单列表')

        def walk(nodes):
            for n in nodes:
                if n['id'] == self.menu_id:
                    return n
                found = walk(n.get('children') or [])
                if found:
                    return found
        self.assertIsNotNone(walk(body['result']), '新菜单应在列表树中')

    def test_03_route_tree_contains(self):
        body = self.assertOk(self.client.get('/menu/route/tree/'), '路由树')
        paths = []

        def walk(nodes):
            for n in nodes:
                paths.append(n.get('path'))
                walk(n.get('children') or [])
        walk(body['result'])
        self.assertIn(self.path, paths)

    def test_04_update(self):
        body = self.assertOk(self.client.put(f'/menu/{self.menu_id}/', json={
            'title': '接口测试菜单-改', 'path': self.path, 'type': 1, 'status': True,
        }), '更新菜单')
        self.assertEqual(body['result']['title'], '接口测试菜单-改')

    def test_05_delete(self):
        self.assertOk(self.client.delete(f'/menu/{self.menu_id}/'), '删除菜单')
        MenuFlowTest.menu_id = None


if __name__ == '__main__':
    unittest.main()
