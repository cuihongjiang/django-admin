# -*- coding: utf-8 -*-
# @Time    : 2025/09/20 1:31
# @Author  : 崔宏江
# @FileName: user.py
# @Software: PyCharm
# -*- coding: utf-8 -*-
from rest_framework.viewsets import ViewSet
from JsAdmin.models import Users
from JsAdmin.serializers.user_serializers import SchemaOut, SchemaIn
from utils.pagination import MyPagination
from utils.response_utils import ResponseUtils
from rest_framework.decorators import action

class UserViewSet(ViewSet):
    pagination_class = MyPagination

    def create(self, request):
        # 1. 使用 data 参数初始化序列化器
        user_serializer = SchemaIn(data=request.data)

        # 2. 验证数据，如果失败则自动返回 400 错误
        user_serializer.is_valid(raise_exception=True)

        # 3. 调用 .save() 方法，它会自动调用序列化器的 .create() 方法
        #    并返回新创建的用户实例
        new_user = user_serializer.save()

        # 4. 使用输出序列化器 (SchemaOut) 来格式化返回数据
        #    这是一个好习惯，可以控制对外暴露的字段
        output_serializer = SchemaOut(new_user)

        # 5. 返回成功响应，状态码应为 201 Created
        return ResponseUtils.success(
            data=output_serializer.data,
            msg="用户创建成功",
            # 如果你的 ResponseUtils 支持自定义状态码，最好设置为 201
            # status_code=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        try:
            # 1. 获取要更新的实例
            instance = Users.objects.get(pk=pk)
        except Users.DoesNotExist:
            return ResponseUtils.error(msg="User not found", status_code=404)

        # 2. 初始化序列化器，传入实例和要更新的数据
        user_serializer = SchemaIn(instance, data=request.data, partial=True)

        # 3. 验证数据
        if user_serializer.is_valid():
            # 4. 调用 .save() 方法，它会自动更新 instance 并返回更新后的实例
            updated_user = user_serializer.save()

            # 5. 使用输出序列化器序列化更新后的数据（这是一个好习惯）
            output_serializer = SchemaOut(updated_user)

            return ResponseUtils.success(data=output_serializer.data, msg="用户更新成功")
        else:
            # 如果验证失败，返回错误信息
            return ResponseUtils.error( msg="数据验证失败", status_code=400)

    @action(detail=True, methods=["DELETE"])
    def delete_user(self, request, pk=None):
        instance = Users.objects.all()
        instance.delete()
        return ResponseUtils.success(msg="用户删除成功")

    def retrieve(self, request, pk=None):
        try:
            instance = Users.objects.get(pk=pk)  # 通过pk获取单个用户
            user_serializer = SchemaOut(instance)
            return ResponseUtils.success(data=user_serializer.data)
        except Users.DoesNotExist:
            return ResponseUtils.error( "用户不存在", code=404,status_code=404)

    def list(self, request):
        queryset = Users.objects.all()
        user_serializer =SchemaOut(queryset, many=True)
        return ResponseUtils.success(data=user_serializer.data)

    @action(detail=True, methods=["POST"])
    def set_password(self, request, pk=None):
        instance = Users.objects.get(pk=pk)
        data = request.data
        if instance.id == data["id"]:
            instance.set_password(data["password"])
            instance.save()
            return ResponseUtils.success(msg="密码修改成功")
        else:
            return ResponseUtils.permission_denied(msg="只能修改自己的密码")

    @action(detail=True, methods=["PUT"])
    def reset_password(self, request, pk=None):
        instance = Users.objects.all()
        instance.set_password("123456")
        instance.save()
        return ResponseUtils.success(msg="密码重置成功")
