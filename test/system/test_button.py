# -*- coding: utf-8 -*-
"""
权限标识（Button）管理测试：CRUD
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase


class ButtonFlowTest(APITestCase):

    code = 'api:test:btn'

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'button_id', None):
            cls.client.delete(f'/button/{cls.button_id}/')

    def test_01_create(self):
        body = self.assertOk(self.client.post('/button/', json={
            'name': '接口测试权限', 'code': self.code, 'status': True,
        }), '创建权限标识')
        ButtonFlowTest.button_id = body['result']['id']

    def test_02_list_filter(self):
        body = self.assertOk(self.client.get('/button/', params={'code': self.code}), '列表过滤')
        self.assertEqual(len(body['result']), 1)

    def test_03_update(self):
        body = self.assertOk(self.client.put(f'/button/{self.button_id}/', json={
            'name': '接口测试权限-改', 'code': self.code, 'status': True,
        }), '更新权限标识')
        self.assertEqual(body['result']['name'], '接口测试权限-改')

    def test_04_delete(self):
        self.assertOk(self.client.delete(f'/button/{self.button_id}/'), '删除权限标识')
        ButtonFlowTest.button_id = None


if __name__ == '__main__':
    unittest.main()
