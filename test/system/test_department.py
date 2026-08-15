# -*- coding: utf-8 -*-
"""
部门管理测试：CRUD + 树形结构
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase


class DepartmentFlowTest(APITestCase):

    dept_name = '接口测试部门'

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'dept_id', None):
            cls.client.delete(f'/department/{cls.dept_id}/')

    def test_01_create(self):
        body = self.assertOk(self.client.post('/department/', json={'name': self.dept_name, 'status': True}), '创建部门')
        DepartmentFlowTest.dept_id = body['result']['id']

    def test_02_tree_contains(self):
        body = self.assertOk(self.client.get('/department/list/tree/'), '部门树')
        names = []

        def walk(nodes):
            for n in nodes:
                names.append(n['name'])
                walk(n.get('children') or [])
        walk(body['result'])
        self.assertIn(self.dept_name, names)

    def test_03_update(self):
        body = self.assertOk(self.client.put(f'/department/{self.dept_id}/', json={
            'name': self.dept_name, 'owner': '测试负责人', 'status': True,
        }), '更新部门')
        self.assertEqual(body['result']['owner'], '测试负责人')

    def test_04_filter_by_name(self):
        body = self.assertOk(self.client.get('/department/', params={'name': self.dept_name}), '按名称过滤')
        self.assertTrue(all(d['name'] == self.dept_name for d in body['result']))
        self.assertGreaterEqual(len(body['result']), 1)

    def test_05_delete(self):
        self.assertOk(self.client.delete(f'/department/{self.dept_id}/'), '删除部门')
        DepartmentFlowTest.dept_id = None


if __name__ == '__main__':
    unittest.main()
