# -*- coding: utf-8 -*-
# @Time    : 2025/09/20 1:31
# @Author  : 崔宏江
# @FileName: user.py
# @Software: PyCharm
# -*- coding: utf-8 -*-
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from JsAdmin.models import Users
from JsAdmin.serializers.user_serializers import SchemaOut, SchemaIn
from utils.pagination import MyPagination
from utils.response_utils import ResponseUtils
from utils.permission import IsAdminOrSuperuser, IsOwnerOrAdmin


class UserViewSet(ModelViewSet):
    """
    用户管理视图集
    提供用户的 CRUD 操作和密码管理
    """
    queryset = Users.objects.all()
    serializer_class = SchemaIn
    pagination_class = MyPagination

    def get_serializer_class(self):
        """
        根据操作类型返回不同的序列化器
        读操作使用 SchemaOut，写操作使用 SchemaIn
        """
        if self.action in ['list', 'retrieve']:
            return SchemaOut
        return SchemaIn

    def perform_create(self, serializer):
        """创建用户后的处理"""
        serializer.save()

    def perform_update(self, serializer):
        """更新用户后的处理"""
        serializer.save()

    def create(self, request, *args, **kwargs):
        """创建用户"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        output_serializer = SchemaOut(serializer.instance)
        return ResponseUtils.success(
            data=output_serializer.data,
            msg="用户创建成功"
        )

    def update(self, request, *args, **kwargs):
        """更新用户"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        output_serializer = SchemaOut(serializer.instance)
        return ResponseUtils.success(
            data=output_serializer.data,
            msg="用户更新成功"
        )

    def destroy(self, request, *args, **kwargs):
        """删除用户"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return ResponseUtils.success(msg="用户删除成功")

    def retrieve(self, request, *args, **kwargs):
        """获取单个用户"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ResponseUtils.success(data=serializer.data)

    def list(self, request, *args, **kwargs):
        """获取用户列表"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return ResponseUtils.success(data=serializer.data)

    @action(detail=True, methods=["POST"], permission_classes=[IsOwnerOrAdmin])
    def set_password(self, request, pk=None):
        """
        修改密码（用户自己或管理员）
        POST /api/user/{id}/set_password/
        请求参数: {"password": "new_password"}
        """
        instance = self.get_object()
        password = request.data.get("password")
        
        if not password:
            return ResponseUtils.error(
                msg="密码不能为空", 
                code=400, 
                status_code=400
            )

        instance.set_password(password)
        instance.save()
        return ResponseUtils.success(msg="密码修改成功")

    @action(detail=True, methods=["PUT"], permission_classes=[IsAdminOrSuperuser])
    def reset_password(self, request, pk=None):
        """
        重置密码（仅管理员）
        PUT /api/user/{id}/reset_password/
        将用户密码重置为 123456
        """
        instance = self.get_object()
        default_password = "123456"
        instance.set_password(default_password)
        instance.save()
        return ResponseUtils.success(
            msg=f"密码已重置为: {default_password}"
        )
