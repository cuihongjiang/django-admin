# -*- coding: utf-8 -*-
"""
分类字典（CategoryDict）测试：CRUD + 树形查询
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase


class CategoryDictFlowTest(APITestCase):

    code = 'api_test_category'

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'cat_id', None):
            cls.client.delete(f'/categorydict/{cls.cat_id}/')

    def test_01_create(self):
        body = self.assertOk(self.client.post('/categorydict/', json={
            'label': '接口测试分类', 'value': 'api-test', 'code': self.code,
        }), '创建分类')
        CategoryDictFlowTest.cat_id = body['result']['id']

    def test_02_tree(self):
        body = self.assertOk(self.client.get('/categorydict/list/tree/'), '分类树')
        labels = []

        def walk(nodes):
            for n in nodes:
                labels.append(n['label'])
                walk(n.get('children') or [])
        walk(body['result'])
        self.assertIn('接口测试分类', labels)

    def test_03_update(self):
        body = self.assertOk(self.client.put(f'/categorydict/{self.cat_id}/', json={
            'label': '接口测试分类-改', 'value': 'api-test', 'code': self.code,
        }), '更新分类')
        self.assertEqual(body['result']['label'], '接口测试分类-改')

    def test_04_delete(self):
        self.assertOk(self.client.delete(f'/categorydict/{self.cat_id}/'), '删除分类')
        CategoryDictFlowTest.cat_id = None


if __name__ == '__main__':
    unittest.main()
