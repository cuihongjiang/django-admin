# -*- coding: utf-8 -*-
"""
数据字典（Dict）管理测试：CRUD
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase


class DictFlowTest(APITestCase):

    code = 'api_test_dict'

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'dict_id', None):
            cls.client.delete(f'/dictionary/{cls.dict_id}/')

    def test_01_create(self):
        body = self.assertOk(self.client.post('/dictionary/', json={
            'name': '接口测试字典', 'code': self.code, 'status': True,
        }), '创建字典')
        DictFlowTest.dict_id = body['result']['id']

    def test_02_list_filter(self):
        body = self.assertOk(self.client.get('/dictionary/', params={'code': self.code}), '列表过滤')
        self.assertEqual(len(body['result']), 1)

    def test_03_update(self):
        body = self.assertOk(self.client.put(f'/dictionary/{self.dict_id}/', json={
            'name': '接口测试字典-改', 'code': self.code, 'status': True,
        }), '更新字典')
        self.assertEqual(body['result']['name'], '接口测试字典-改')

    def test_04_delete(self):
        self.assertOk(self.client.delete(f'/dictionary/{self.dict_id}/'), '删除字典')
        DictFlowTest.dict_id = None


if __name__ == '__main__':
    unittest.main()
