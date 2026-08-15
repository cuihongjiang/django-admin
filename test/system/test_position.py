# -*- coding: utf-8 -*-
"""
岗位管理测试：CRUD + Excel 导入导出
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase


class PositionFlowTest(APITestCase):

    code = 'API_TEST_POST'

    @classmethod
    def tearDownClass(cls):
        # 导入测试会产生重复行，按编码全部清理
        body = cls.client.get('/position/', params={'code': cls.code}).json()
        for item in body.get('result') or []:
            cls.client.delete(f"/position/{item['id']}/")

    def test_01_create(self):
        body = self.assertOk(self.client.post('/position/', json={
            'name': '接口测试岗位', 'code': self.code, 'status': 1, 'sort': 99,
        }), '创建岗位')
        PositionFlowTest.position_id = body['result']['id']

    def test_02_list_and_detail(self):
        body = self.assertOk(self.client.get('/position/', params={'code': self.code}), '列表过滤')
        self.assertEqual(len(body['result']), 1)
        body = self.assertOk(self.client.get(f'/position/{self.position_id}/'), '详情')
        self.assertEqual(body['result']['code'], self.code)

    def test_03_update(self):
        body = self.assertOk(self.client.put(f'/position/{self.position_id}/', json={
            'name': '接口测试岗位-改', 'code': self.code, 'status': 1, 'sort': 98,
        }), '更新岗位')
        self.assertEqual(body['result']['name'], '接口测试岗位-改')

    def test_04_export(self):
        resp = self.client.get('/position/all/export/')
        self.assertEqual(resp.status_code, 200, '导出应 200')
        self.assertIn('spreadsheetml', resp.headers.get('Content-Type', ''), '应为 xlsx 类型')
        self.assertGreater(len(resp.content), 100, '导出内容非空')
        PositionFlowTest.export_bytes = resp.content

    def test_05_import(self):
        """导出文件重新导入（追加一行同编码数据，tearDownClass 统一清理）"""
        resp = self.client.post('/position/all/import/', files={
            'file': ('positions.xlsx', self.export_bytes,
                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
        })
        self.assertOk(resp, '导入 Excel')

    def test_06_delete(self):
        self.assertOk(self.client.delete(f'/position/{self.position_id}/'), '删除岗位')
        resp = self.client.get(f'/position/{self.position_id}/')
        self.assertEqual(resp.status_code, 404, '删除后应 404')
        PositionFlowTest.position_id = None


if __name__ == '__main__':
    unittest.main()
