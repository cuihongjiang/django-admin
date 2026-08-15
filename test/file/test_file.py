# -*- coding: utf-8 -*-
"""
文件模块测试：上传 / 下载 / 图片预览 / 删除
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase

UPLOAD_CONTENT = b'api test file upload content'


class FileFlowTest(APITestCase):

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'file_id', None):
            cls.client.delete(f'/file/{cls.file_id}/')

    def test_01_upload(self):
        resp = self.client.post('/file/upload/', files={'file': ('api_test.txt', UPLOAD_CONTENT, 'text/plain')})
        body = self.assertOk(resp, '上传文件')
        FileFlowTest.file_id = body['result']['id']
        self.assertEqual(body['result']['name'], 'api_test.txt')

    def test_02_list_and_detail(self):
        self.assertOk(self.client.get('/file/'), '文件列表')
        body = self.assertOk(self.client.get(f'/file/{self.file_id}/'), '文件详情')
        self.assertEqual(body['result']['name'], 'api_test.txt')

    def test_03_download(self):
        """下载内容与上传内容一致"""
        resp = self.client.get(f'/file/{self.file_id}/download/')
        self.assertEqual(resp.status_code, 200, '下载应 200')
        self.assertEqual(resp.content, UPLOAD_CONTENT, '下载内容应与上传一致')

    def test_04_image(self):
        resp = self.client.get(f'/file/{self.file_id}/image/')
        self.assertEqual(resp.status_code, 200, '图片预览应 200')

    def test_05_delete(self):
        self.assertOk(self.client.delete(f'/file/{self.file_id}/'), '删除文件')
        resp = self.client.get(f'/file/{self.file_id}/')
        self.assertEqual(resp.status_code, 404, '删除后应 404')
        FileFlowTest.file_id = None


if __name__ == '__main__':
    unittest.main()
