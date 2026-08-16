# -*- coding: utf-8 -*-
"""
项目初始化命令
"""
import importlib
import logging

from django.core.management.base import BaseCommand

from manageSys import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    项目初始化命令: python manage.py init
    """

    def add_arguments(self, parser):
        parser.add_argument('init_name', nargs='*', type=str, )
        parser.add_argument('-y', nargs='*')
        parser.add_argument('-Y', nargs='*')
        parser.add_argument('-n', nargs='*')
        parser.add_argument('-N', nargs='*')

    def handle(self, *args, **options):
        reset = False
        if isinstance(options.get('y'), list) or isinstance(options.get('Y'), list):
            reset = True
        if isinstance(options.get('n'), list) or isinstance(options.get('N'), list):
            reset = False
        self.stdout.write(f"正在准备初始化数据，{'如有初始化数据，将会不做操作跳过' if not reset else '初始数据将会先删除后新增'}...")

        for app in settings.INSTALLED_APPS:
            module_name = f'{app}.initialize'
            try:
                module = importlib.import_module(module_name)
            except ModuleNotFoundError as e:
                if e.name == module_name:
                    logger.debug(f"{app} 无初始化模块: {str(e)}")
                    continue
                # initialize 模块内部依赖缺失属于真实错误，暴露出来而不是静默跳过
                raise
            if hasattr(module, 'main'):
                module.main(reset=reset)
        self.stdout.write(self.style.SUCCESS("初始化数据完成！"))
