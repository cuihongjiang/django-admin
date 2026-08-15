# -*- coding: utf-8 -*-
"""
字典项（DictItem）测试：CRUD + 按字典编码查询
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase


class DictItemFlowTest(APITestCase):

    code = 'api_test_dict_item'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        body = cls.client.post('/dictionary/', json={
            'name': '字典项测试字典', 'code': cls.code, 'status': True,
        }).json()
        cls.dict_id = body['result']['id']

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'item_id', None):
            cls.client.delete(f'/dictitem/{cls.item_id}/')
        if getattr(cls, 'dict_id', None):
            cls.client.delete(f'/dictionary/{cls.dict_id}/')

    def test_01_create_item(self):
        body = self.assertOk(self.client.post('/dictitem/', json={
            'dict': self.dict_id, 'label': '选项一', 'value': '1', 'status': True,
        }), '创建字典项')
        DictItemFlowTest.item_id = body['result']['id']

    def test_02_by_code(self):
        """按字典编码查询启用的字典项"""
        body = self.assertOk(self.client.get('/dictitem/by/code/', params={'code': self.code}), '按编码查询')
        labels = [i['label'] for i in body['result']]
        self.assertIn('选项一', labels)

    def test_03_by_code_missing_param(self):
        resp = self.client.get('/dictitem/by/code/')
        self.assertErr(resp, 400, 400, '缺少 code')

    def test_04_by_code_not_found(self):
        """不存在的编码返回空数组而非报错"""
        body = self.assertOk(self.client.get('/dictitem/by/code/', params={'code': 'no_such_dict'}), '不存在编码')
        self.assertEqual(body['result'], [])

    def test_05_update_item(self):
        body = self.assertOk(self.client.put(f'/dictitem/{self.item_id}/', json={
            'dict': self.dict_id, 'label': '选项一-改', 'value': '1', 'status': True,
        }), '更新字典项')
        self.assertEqual(body['result']['label'], '选项一-改')

    def test_06_delete_item(self):
        self.assertOk(self.client.delete(f'/dictitem/{self.item_id}/'), '删除字典项')
        DictItemFlowTest.item_id = None


if __name__ == '__main__':
    unittest.main()
