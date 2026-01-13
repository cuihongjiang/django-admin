# # -*- coding: utf-8 -*-
# # @Time    : 2024/12/7 00:24
# # @Author  : 崔宏江
# # @FileName: dept.py
# # @Software: VSCode
#
# from typing import List
#
# from django.shortcuts import get_object_or_404
# from ninja import Field, ModelSchema, Query, Router, Schema
# from ninja.pagination import paginate
# from JsAdmin.models import Dept
# from utils.js_crud import create, delete, retrieve, update
# from utils.js_ninja import JsFilters, MyPagination
# from utils.js_json_renderer import JsJSONRenderer
# from utils.list_to_tree import list_to_route, list_to_tree
#
# router = Router()
#
#
# class Filters(JsFilters):
#     name: str = Field(None, alias="name")
#     status: bool = Field(None, alias="status")
#     id: str = Field(None, alias="id")
#
#
# class SchemaIn(ModelSchema):
#     parent_id: int = None
#
#     class Config:
#         model = Dept
#         model_exclude = ['id', 'parent', 'create_datetime', 'update_datetime']
#
#
# class SchemaOut(ModelSchema):
#     class Config:
#         model = Dept
#         model_fields = "__all__"
#     # model_fields = []
#
#
# @router.post("/dept", response=SchemaOut)
# def create_dept(request, data: SchemaIn):
#     dept = create(request, data, Dept)
#     return dept
#
#
# @router.delete("/dept/{dept_id}")
# def delete_dept(request, dept_id: int):
#     delete(dept_id, Dept)
#     return {"success": True}
#
#
# @router.put("/dept/{dept_id}", response=SchemaOut)
# def update_dept(request, dept_id: int, data: SchemaIn):
#     dept = update(request, dept_id, data, Dept)
#     return dept
#
#
# @router.get("/dept", response=List[SchemaOut])
# @paginate(MyPagination)
# def list_dept(request, filters: Filters = Query(...)):
#     qs = retrieve(request, Dept, filters)
#     return qs
#
#
# @router.get("/dept/{dept_id}", response=SchemaOut)
# def get_dept(request, dept_id: int):
#     dept = get_object_or_404(Dept, id=dept_id)
#     return dept
#
#
# @router.get("/dept/list/tree")
# def list_dept_tree(request, filters: Filters = Query(...)):
#     qs = retrieve(request, Dept, filters).values()
#     dept_tree = list_to_tree(list(qs))
#     return JsJSONRenderer(data=dept_tree)
