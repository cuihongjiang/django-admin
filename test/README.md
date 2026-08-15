# 接口测试

基于 Python `unittest` + `requests` 的 HTTP 接口测试，覆盖全部 API 模块。

## 目录结构

```
test/
    run_all.py        主测试入口
    client.py         共享 API 客户端（登录 / 鉴权请求封装）
    base.py           测试基类（自动登录 + 断言助手）
    auth/             认证：登录 / 刷新 token / 退出
    system/           系统管理：用户 / 部门 / 岗位 / 角色 / 菜单 / 按钮 / 列字段 / 生成器
    data_dict/        数据字典：字典 / 字典项 / 分类字典
    log/              日志：登录日志 / 操作日志（只读）
    file/             文件：上传 / 下载 / 图片预览
    monitor/          系统监控（只读）
```

## 运行方式

先启动开发服务器：

```bash
.venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000
```

运行测试（另开终端，在项目根目录执行）：

```bash
.venv/Scripts/python.exe test/run_all.py            # 全部模块
.venv/Scripts/python.exe test/run_all.py auth system  # 指定模块
.venv/Scripts/python.exe test/system/test_user.py   # 单个脚本
```

## 配置

默认连接 `http://127.0.0.1:8000/api`，账号 `superadmin/123456`，
可用环境变量覆盖：`API_BASE` / `API_USER` / `API_PASSWORD`。

## 说明

- 写操作测试均创建自有数据并在结束时清理，不影响种子数据
- 同一测试类内的方法按 `test_01_`、`test_02_` 编号顺序执行（生命周期类用例）
- 登录/日志/监控等只读模块不修改任何数据
