# -*- coding: utf-8 -*-
"""
低代码生成器测试：表清单 / 模板 CRUD / 代码预览 / zip 下载 / 菜单生成（幂等）
"""
import io
import sys
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase

# 以 Post 模型为生成目标的测试配置
TEMPLATE_PAYLOAD = {
    'name': '接口测试生成模板',
    'code': 'api_test_gen',
    'app_label': 'system',
    'model_name': 'Post',
    'table_info': [
        {'field': 'name', 'title': '岗位名称', 'is_search': True, 'is_list': True, 'width': 150},
        {'field': 'code', 'title': '岗位编码', 'is_search': True, 'is_list': True, 'width': 120},
    ],
    'form_info': [
        {'field': 'name', 'title': '岗位名称', 'component': 'input', 'required': True},
        {'field': 'status', 'title': '岗位状态', 'component': 'switch'},
    ],
}


class GeneratorFlowTest(APITestCase):

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'menu_id', None):
            cls.client.delete(f'/menu/{cls.menu_id}/')
        if getattr(cls, 'template_id', None):
            cls.client.delete(f'/generator/{cls.template_id}/')

    def test_01_tables(self):
        body = self.assertOk(self.client.get('/generator/tables/'), '模型表清单')
        models = {t['model'] for t in body['result']}
        self.assertIn('Post', models)
        post_table = next(t for t in body['result'] if t['model'] == 'Post')
        self.assertTrue(post_table['fields'], 'Post 表应有字段列表')

    def test_02_create_template(self):
        body = self.assertOk(self.client.post('/generator/', json=TEMPLATE_PAYLOAD), '创建模板')
        GeneratorFlowTest.template_id = body['result']['id']
        # 返回的配置应还原为数组
        self.assertIsInstance(body['result']['table_info'], list)

    def test_03_create_invalid_config(self):
        """table_info 非数组返回 400"""
        bad = dict(TEMPLATE_PAYLOAD, table_info='not-json-array')
        resp = self.client.post('/generator/', json=bad)
        self.assertEqual(resp.status_code, 400)

    def test_04_preview(self):
        body = self.assertOk(self.client.post(f'/generator/{self.template_id}/code/preview/'), '代码预览')
        paths = [f['path'] for f in body['result']]
        self.assertEqual(len(paths), 5, '应生成 5 个文件')
        self.assertIn('frontend/api_test_gen/index.vue', paths)
        vue = next(f for f in body['result'] if f['path'].endswith('index.vue'))['content']
        self.assertIn('岗位名称', vue, 'Vue 页面应包含配置的列标题')

    def test_05_download(self):
        resp = self.client.get(f'/generator/{self.template_id}/code/download/')
        self.assertEqual(resp.status_code, 200, '下载应 200')
        self.assertEqual(resp.headers.get('Content-Type'), 'application/zip')
        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        self.assertIsNone(zf.testzip(), 'zip 应完整')
        self.assertEqual(len(zf.namelist()), 5)

    def test_06_menu_create(self):
        body = self.assertOk(self.client.post(f'/generator/{self.template_id}/menu/create/', json={}), '生成菜单')
        GeneratorFlowTest.menu_id = body['result']['menu_id']
        self.assertTrue(body['result']['created'])
        self.assertEqual(len(body['result']['button_ids']), 4, '应有查/增/改/删 4 个按钮')

    def test_07_menu_create_idempotent(self):
        """重复生成不重复创建"""
        body = self.assertOk(self.client.post(f'/generator/{self.template_id}/menu/create/', json={}), '幂等生成')
        self.assertFalse(body['result']['created'])
        self.assertEqual(body['result']['menu_id'], self.menu_id)

    def test_08_template_has_menu_flag(self):
        body = self.assertOk(self.client.get(f'/generator/{self.template_id}/'), '模板详情')
        self.assertTrue(body['result']['has_menu'])

    def test_09_cleanup(self):
        """删除菜单（级联按钮）和模板"""
        self.assertOk(self.client.delete(f'/menu/{self.menu_id}/'), '删除生成的菜单')
        self.assertOk(self.client.delete(f'/generator/{self.template_id}/'), '删除模板')
        GeneratorFlowTest.menu_id = None
        GeneratorFlowTest.template_id = None


if __name__ == '__main__':
    unittest.main()
