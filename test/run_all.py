# -*- coding: utf-8 -*-
"""
接口测试主入口

用法：
    python test/run_all.py              # 运行全部模块测试
    python test/run_all.py auth system  # 只运行指定模块目录

前提：开发服务器已启动（默认 http://127.0.0.1:8000，可用 API_BASE 覆盖）
"""
import sys
import unittest
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))


def build_suite(modules=None):
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for d in sorted(TEST_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith('_') or d.name == '__pycache__':
            continue
        if modules and d.name not in modules:
            continue
        suite.addTests(loader.discover(str(d), pattern='test_*.py', top_level_dir=str(PROJECT_ROOT)))
    return suite


def main():
    modules = sys.argv[1:] or None
    suite = build_suite(modules)
    tests = suite.countTestCases()
    if tests == 0:
        print('未发现测试用例')
        sys.exit(1)
    print(f'共发现 {tests} 个测试用例\n')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print(f'\n结果: {result.testsRun - len(result.failures) - len(result.errors)} 通过, '
          f'{len(result.failures)} 失败, {len(result.errors)} 错误')
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
