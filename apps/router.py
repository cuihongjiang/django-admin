# -*- coding: utf-8 -*-
"""
API 路由配置
"""
from rest_framework.routers import DefaultRouter

from apps.auth.apis.login import LoginViewSet
from apps.data_dict.apis.category_dict import CategoryDictViewSet
from apps.data_dict.apis.dict import DictViewSet
from apps.data_dict.apis.dict_item import DictItemViewSet
from apps.file.apis.file import FileViewSet
from apps.log.apis.login_log import LoginLogViewSet
from apps.log.apis.operation_log import OperationLogViewSet
from apps.monitor.apis.monitor import MonitorView
from apps.system.apis.button import ButtonViewSet
from apps.system.apis.dept import DeptViewSet
from apps.system.apis.generator import GeneratorTemplateViewSet
from apps.system.apis.menu import MenuViewSet
from apps.system.apis.menu_button import MenuButtonViewSet
from apps.system.apis.menu_column import MenuColumnFieldViewSet
from apps.system.apis.post import PostViewSet
from apps.system.apis.role import RoleViewSet
from apps.system.apis.system_config import SystemConfigViewSet
from apps.system.apis.user import UserViewSet
from apps.system.apis.white_list import ApiWhiteListViewSet

api_router = DefaultRouter()
# 认证
api_router.register(r'login', LoginViewSet, basename='login')
# 系统管理
api_router.register(r'user', UserViewSet, basename='user')
api_router.register(r'department', DeptViewSet, basename='department')
api_router.register(r'position', PostViewSet, basename='position')
api_router.register(r'role', RoleViewSet, basename='role')
api_router.register(r'menu', MenuViewSet, basename='menu')
api_router.register(r'button', ButtonViewSet, basename='button')
api_router.register(r'menubutton', MenuButtonViewSet, basename='menubutton')
api_router.register(r'menucolumnfield', MenuColumnFieldViewSet, basename='menucolumnfield')
# 接口白名单 / 系统配置（表驱动，页面可管理）
api_router.register(r'apiwhitelist', ApiWhiteListViewSet, basename='apiwhitelist')
api_router.register(r'systemconfig', SystemConfigViewSet, basename='systemconfig')
# 低代码生成器
api_router.register(r'generator', GeneratorTemplateViewSet, basename='generator')
# 数据字典
api_router.register(r'dictionary', DictViewSet, basename='dictionary')
api_router.register(r'dictitem', DictItemViewSet, basename='dictitem')
api_router.register(r'categorydict', CategoryDictViewSet, basename='categorydict')
# 日志
api_router.register(r'loginlog', LoginLogViewSet, basename='loginlog')
api_router.register(r'operationlog', OperationLogViewSet, basename='operationlog')
# 文件与监控
api_router.register(r'file', FileViewSet, basename='file')
api_router.register(r'monitor', MonitorView, basename='monitor')

# 将下面两行分别加入 apps/router.py（由低代码生成器生成）

from apps.system.apis.notice import NoticeViewSet

api_router.register(r'notice', NoticeViewSet, basename='notice')
