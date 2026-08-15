# -*- coding: utf-8 -*-
"""
低代码生成器视图集

流程：
1. GET  tables/           查询可生成的模型表
2. POST /api/generator/   保存生成配置（table_info / form_info）
3. POST {id}/code/preview/     预览生成的文件内容
4. GET  {id}/code/download/    下载生成代码 zip 包
5. POST {id}/menu/create/      生成菜单 + 按钮权限（幂等）
"""
import logging

from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

from apps.system.models import GeneratorTemplate, Menu, MenuButton, Role
from apps.system.serializers import GeneratorTemplateSerializer
from utils.generator.builder import build_context, generate_files, generate_zip, to_camel, validate_config
from utils.db.models import get_all_models_objects
from utils.web.response_utils import ResponseUtils
from utils.web.viewsets import CoreModelViewSet

logger = logging.getLogger(__name__)


class MenuCreateIn(serializers.Serializer):
    """menu/create 请求体（仅用于接口文档声明）"""
    parent_id = serializers.IntegerField(required=False, help_text='上级菜单 id，缺省为顶级')
    role_ids = serializers.ListField(child=serializers.IntegerField(), required=False,
                                     help_text='需要授权的角色 id 列表')


class GeneratorTemplateViewSet(CoreModelViewSet):
    """
    低代码生成器视图集
    模板配置 CRUD + 代码预览/下载 + 菜单按钮生成
    """
    queryset = GeneratorTemplate.objects.all()
    serializer_class = GeneratorTemplateSerializer
    filter_fields = ['name', 'code', 'has_menu']

    def _validate(self, request):
        """创建/更新前校验配置 JSON 结构"""
        validate_config(
            request.data.get('table_info', ''),
            request.data.get('form_info', ''),
        )

    def create(self, request, *args, **kwargs):
        try:
            self._validate(request)
        except ValueError as e:
            return ResponseUtils.error(msg=str(e), code=400, status_code=400)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            self._validate(request)
        except ValueError as e:
            return ResponseUtils.error(msg=str(e), code=400, status_code=400)
        return super().update(request, *args, **kwargs)

    @extend_schema(request=None)
    @action(detail=False, methods=['get'])
    def tables(self, request):
        """
        查询所有可生成的模型表及字段
        GET /api/generator/tables/
        排除 Django 内置应用（auth/contenttypes/admin/sessions）
        """
        result = []
        for model_name, info in get_all_models_objects().items():
            model = info['object']
            app_label = model._meta.app_label
            if app_label in ('auth', 'contenttypes', 'admin', 'sessions'):
                continue
            result.append({
                'model': model_name,
                'app_label': app_label,
                'table_name': info['table']['table'],
                'title': info['table']['tableName'],
                'fields': info['table']['tableFields'],
            })
        return ResponseUtils.success(data=result)

    @extend_schema(request=None)
    @action(detail=True, methods=['post'], url_path='code/preview')
    def code_preview(self, request, pk=None):
        """
        预览生成的代码
        POST /api/generator/{id}/code/preview/
        返回 [{path, content}] 文件数组
        """
        template = self.get_object()
        try:
            files = generate_files(template)
        except Exception:
            logger.exception('代码生成失败 template_id=%s', template.id)
            return ResponseUtils.error(msg="代码生成失败，请检查模板配置", code=500, status_code=500)
        return ResponseUtils.success(data=files, msg=f"共生成 {len(files)} 个文件")

    @extend_schema(request=None)
    @action(detail=True, methods=['get'], url_path='code/download')
    def code_download(self, request, pk=None):
        """
        下载生成的代码 zip 包
        GET /api/generator/{id}/code/download/
        """
        template = self.get_object()
        try:
            zip_bytes = generate_zip(template)
        except Exception:
            logger.exception('代码打包失败 template_id=%s', template.id)
            return ResponseUtils.error(msg="代码打包失败，请检查模板配置", code=500, status_code=500)
        response = HttpResponse(zip_bytes, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{template.code}.zip"'
        return response

    @extend_schema(request=MenuCreateIn)
    @action(detail=True, methods=['post'], url_path='menu/create')
    def menu_create(self, request, pk=None):
        """
        生成菜单和按钮权限（幂等，重复调用不会重复创建）
        POST /api/generator/{id}/menu/create/
        请求参数: {"parent_id": 1, "role_ids": [1, 2]}
        """
        template = self.get_object()
        context = build_context(template)
        code = context['code']

        parent_id = request.data.get('parent_id')
        role_ids = request.data.get('role_ids') or []

        # 1. 菜单（按 path+component 幂等）
        menu, menu_created = Menu.objects.get_or_create(
            path=f'/{code}',
            component=f'/{code}/index',
            defaults={
                'title': template.name or code,
                'name': to_camel(code),
                'icon': 'ant-design:code-outlined',
                'type': 1,
                'status': True,
                'parent_id': parent_id,
                'creator': request.user if getattr(request.user, 'is_authenticated', False) else None,
                'modifier': getattr(request.user, 'username', None),
            },
        )

        # 2. 四个 CRUD 按钮权限（按 menu+api+method 幂等）
        button_defs = [
            ('查询', f'{code}:search', f'/api/{code}/', 0),
            ('新增', f'{code}:add', f'/api/{code}/', 1),
            ('修改', f'{code}:update', f'/api/{code}/{{id}}', 2),
            ('删除', f'{code}:delete', f'/api/{code}/{{id}}', 3),
        ]
        buttons = []
        for name, perm_code, api, method in button_defs:
            button, _ = MenuButton.objects.get_or_create(
                menu=menu, api=api, method=method,
                defaults={
                    'name': name,
                    'code': perm_code,
                    'creator': request.user if getattr(request.user, 'is_authenticated', False) else None,
                    'modifier': getattr(request.user, 'username', None),
                },
            )
            buttons.append(button)

        # 3. 授权给指定角色（超管无需授权天然可见）
        roles = Role.objects.filter(id__in=role_ids)
        for role in roles:
            role.menu.add(menu)
            role.permission.add(*buttons)

        # 4. 标记已生成菜单
        if not template.has_menu:
            template.has_menu = True
            template.save(update_fields=['has_menu'])

        msg = '菜单已生成' if menu_created else '菜单已存在，按钮权限已补全'
        if roles:
            msg += f'，已授权 {len(roles)} 个角色'
        logger.info('生成菜单 menu_id=%s code=%s operator=%s',
                    menu.id, code, getattr(request.user, 'username', None))
        return ResponseUtils.success(data={
            'menu_id': menu.id,
            'button_ids': [b.id for b in buttons],
            'created': menu_created,
        }, msg=msg)
