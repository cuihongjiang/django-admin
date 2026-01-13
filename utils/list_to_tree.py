# -*- coding: utf-8 -*-
# @Time    : 2024/12/7 00:24
# @Author  : 崔宏江
# @FileName: list_to_tree.py
# @Software: VSCode
from functools import lru_cache


def add_node(p, node):
    # ⼦节点list
    p["children"] = []
    for n in node:
        if n.get("parent_id") == p.get("id"):
            p["children"].append(n)
    # 递归⼦节点，查找⼦节点的节点
    for t in p["children"]:
        if not t.get("children"):
            t["children"] = []
        t["children"].append(add_node(t, node))
    # 退出递归的条件
    if len(p["children"]) == 0:
        p.pop('children')
        p["choice"] = 1
        return


def list_to_route(data):
    root = []
    node = []
    # 初始化数据，获取根节点和其他子节点list
    for d in data:
        d['meta'] = {
            'title': d.pop('title'),
            'ignoreKeepAlive': d.pop('keepalive'),
            'orderNo': d.pop('sort'),
            'hideMenu': d.pop('hide_menu'),
            'icon': d.pop('icon')
        }

        d["choice"] = 0
        if d.get("parent_id") is None:
            root.append(d)
        else:
            node.append(d)
    # print("root----",root)
    # print("node----",node)
    # 查找子节点
    for p in root:
        add_node(p, node)
    # 无子节点
    if len(root) == 0:
        return node

    return root


@lru_cache(maxsize=128)
def list_to_tree_cache(data: tuple, id_field='id', parent_field='parent_id'):
    """带缓存机制的树结构转换"""
    return list_to_tree(list(data), id_field, parent_field)

def list_to_tree(data):
    root = []
    node = []
    # 初始化数据，获取根节点和其他子节点list

    for d in data:
        d["choice"] = 0
        if d.get("parent_id") is None:
            root.append(d)
        else:
            node.append(d)
    # print("root----",root)
    # print("node----",node)
    # 查找子节点
    for p in root:
        add_node(p, node)
    # 无子节点
    if len(root) == 0:
        return node

    return root
