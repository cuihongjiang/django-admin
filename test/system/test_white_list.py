# -*- coding: utf-8 -*-
"""
接口白名单管理测试：CRUD + 白名单放行语义（前缀匹配 / method 限定 / 缓存即时生效）

黑盒方式验证：匿名请求命中白名单则放行（HTTP 200），未命中被认证拦截（HTTP 401）。
目标路径用 /api/menu/（MenuViewSet 已关闭数据权限，匿名放行后可正常返回）。
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import requests  # noqa: E402

from test.base import APITestCase  # noqa: E402
from test.client import BASE_URL  # noqa: E402


def _anon(method, path):
    """不带认证头的裸请求，返回 HTTP 状态码"""
    return requests.request(method, BASE_URL + path, timeout=30).status_code


class WhiteListFlowTest(APITestCase):

    wl_id = None

    @classmethod
    def tearDownClass(cls):
        if cls.wl_id:
            cls.client.delete(f'/apiwhitelist/{cls.wl_id}/')

    def test_01_whitelist_semantics(self):
        # 未配置白名单：匿名访问被拦截
        self.assertEqual(_anon('GET', '/menu/'), 401, '匿名访问应被认证拦截')

        # 1) method 留空：放行全部方法（GET / POST 均过认证关；POST 过认证后在视图内 403/200 均可，只要不是 401）
        body = self.assertOk(self.client.post('/apiwhitelist/', json={
            'url': '/api/menu/', 'method': None, 'enable_datasource': False,
        }), '创建白名单(method不限)')
        WhiteListFlowTest.wl_id = body['result']['id']
        self.assertEqual(_anon('GET', '/menu/'), 200, 'method 留空应放行 GET')
        self.assertNotEqual(_anon('POST', '/menu/'), 401, 'method 留空应放行 POST（不因认证被拒）')

        # 2) method 限定为 GET：POST 不再放行
        self.assertOk(self.client.put(f'/apiwhitelist/{self.wl_id}/', json={
            'url': '/api/menu/', 'method': 0, 'enable_datasource': False,
        }), '更新白名单(仅GET)')
        self.assertEqual(_anon('GET', '/menu/'), 200, 'method=GET 应放行 GET')
        self.assertEqual(_anon('POST', '/menu/'), 401, 'method=GET 不应放行 POST')

        # 3) 前缀匹配：子路径同样放行
        self.assertEqual(_anon('GET', '/menu/all/list/'), 200, '前缀匹配应放行子路径')

        # 4) 删除后恢复拦截
        self.assertOk(self.client.delete(f'/apiwhitelist/{self.wl_id}/'), '删除白名单')
        WhiteListFlowTest.wl_id = None
        self.assertEqual(_anon('GET', '/menu/'), 401, '删除后匿名访问应恢复拦截')

    def test_02_list_filter(self):
        body = self.assertOk(self.client.get('/apiwhitelist/', params={'url': '/api/login/'}), '列表过滤')
        self.assertTrue(all(item['url'] == '/api/login/' for item in body['result']))
        self.assertGreaterEqual(len(body['result']), 1, '种子白名单 /api/login/ 应存在')


if __name__ == '__main__':
    unittest.main()
