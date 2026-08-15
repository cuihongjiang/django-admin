# -*- coding: utf-8 -*-
"""
菜单列字段（MenuColumnField）测试：批量创建 + 查询 + 删除
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase


class MenuColumnFieldTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        menu = cls.client.post('/menu/', json={
            'title': '列字段测试菜单', 'path': '/api-test-mcf', 'name': 'ApiTestMcf',
            'type': 1, 'status': True,
        }).json()
        cls.menu_id = menu['result']['id']

    @classmethod
    def tearDownClass(cls):
        for fid in getattr(cls, 'field_ids', []):
            cls.client.delete(f'/menucolumnfield/{fid}/')
        if getattr(cls, 'menu_id', None):
            cls.client.delete(f'/menu/{cls.menu_id}/')

    def test_01_batch_create(self):
        body = self.assertOk(self.client.post('/menucolumnfield/batch/create/', json={
            'batch_info': [
                {'menu': self.menu_id, 'name': '名称列', 'code': 'col_name'},
                {'menu': self.menu_id, 'name': '编码列', 'code': 'col_code'},
            ]
        }), '批量创建')
        MenuColumnFieldTest.field_ids = [f['id'] for f in body['result']]
        self.assertEqual(len(self.field_ids), 2)

    def test_02_batch_create_invalid(self):
        """batch_info 非列表返回 400"""
        resp = self.client.post('/menucolumnfield/batch/create/', json={'batch_info': 'not-a-list'})
        self.assertEqual(resp.status_code, 400)

    def test_03_list_filter(self):
        body = self.assertOk(self.client.get('/menucolumnfield/', params={'menu_id': self.menu_id}), '列表过滤')
        codes = {f['code'] for f in body['result']}
        self.assertEqual(codes, {'col_name', 'col_code'})

    def test_04_delete(self):
        for fid in self.field_ids:
            self.assertOk(self.client.delete(f'/menucolumnfield/{fid}/'), '删除列字段')
        MenuColumnFieldTest.field_ids = []


if __name__ == '__main__':
    unittest.main()
