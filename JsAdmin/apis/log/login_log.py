# -*- coding: utf-8 -*-
# @Time    : 2024/12/7 00:24
# @Author  : 崔宏江
# @FileName: login_log.py
# @Software: VSCode
from typing import List

from django.shortcuts import get_object_or_404
from ninja import Field, ModelSchema, Query, Router, Schema
from ninja.pagination import paginate
from JsAdmin.models import LoginLog
from utils.js_crud import create, delete, retrieve, update
from utils.js_ninja import JsFilters, MyPagination

router = Router()


class Filters(JsFilters):
    name: str = Field(None, alias="name")
    code: str = Field(None, alias="code")
    id: str = Field(None, alias="login_log_id")


class SchemaOut(ModelSchema):
    class Config:
        model = LoginLog
        model_fields = "__all__"


@router.delete("/login_log/{login_log_id}")
def delete_login_log(request, login_log_id: int):
    delete(login_log_id, LoginLog)
    return {"success": True}


@router.get("/login_log", response=List[SchemaOut])
@paginate(MyPagination)
def list_login_log(request, filters: Filters = Query(...)):
    qs = retrieve(request, LoginLog, filters)
    return qs


@router.get("/login_log/all/list", response=List[SchemaOut])
def all_list_role(request):
    qs = retrieve(request, LoginLog)
    return qs
