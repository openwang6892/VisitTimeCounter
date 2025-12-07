# 计数器服务

一个简单的HTTP计数器服务，具有以下功能：

- 访问 `/new` 增加计数
- 访问 `/query` 查询总数
- 访问 `/empty` 清空计数
- 计数数据保存在数据库中（PostgreSQL或SQLite）

## 本地使用方法

1. 运行服务：
   ```bash
   python3 counter_service.py
   ```

2. 服务启动后，您可以通过以下方式使用：
   - `GET /new` - 增加计数并返回新值
   - `GET /query` - 查询当前总数
   - `GET /empty` - 清空计数

## 详细API说明

### 增加计数
- `GET /new` - 增加计数1次
- `GET /new?num=5` - 增加计数5次
- `GET /new?to=100` - 计数设置到100（如果当前计数小于100）

### 查询总数
- `GET /query` - 查询总访问次数
- `GET /query?range=today` - 查询今日访问次数
- `GET /query?range=week` - 查询本周访问次数
- `GET /query?range=month` - 查询本月访问次数

### 清空计数
- `GET /empty` - 清空计数到0
- `GET /empty?num=5` - 从当前计数中减去5
- `GET /empty?to=10` - 计数设置到10（如果当前计数大于10）

## 示例

```bash
# 增加计数
curl http://localhost:8000/new

# 增加5次计数
curl "http://localhost:8000/new?num=5"

# 计数设置到100
curl "http://localhost:8000/new?to=100"

# 查询总数
curl http://localhost:8000/query

# 查询今日访问量
curl "http://localhost:8000/query?range=today"

# 查询本周访问量
curl "http://localhost:8000/query?range=week"

# 清空计数
curl http://localhost:8000/empty

# 计数减去5
curl "http://localhost:8000/empty?num=5"

# 计数设置到10
curl "http://localhost:8000/empty?to=10"
```

## 环境变量

- `PORT` - 服务器端口（默认: 8000）
- `DATABASE_URL` - PostgreSQL数据库连接URL（可选，如果不设置则使用SQLite）

## 数据持久化

计数数据会优先保存在PostgreSQL数据库中（通过DATABASE_URL环境变量指定），如果没有配置PostgreSQL则会回退到SQLite数据库 (`counter.db`)。在Render上部署时，配置PostgreSQL数据库可确保数据的完全持久化。

## 依赖

项目依赖于 `psycopg2-binary` 用于PostgreSQL支持：

```bash
pip install -r requirements.txt
```

## Render部署

此项目已配置为可在Render上部署：

1. 将此项目连接到GitHub仓库
2. 在Render上创建Web Service
3. 使用以下设置：
   - 环境: Python
   - 构建命令: `pip install -r requirements.txt`
   - 启动命令: `python counter_service.py`
   - 环境变量（可选）: 配置DATABASE_URL以使用PostgreSQL

## 本地测试

在本地运行服务并测试API：

```bash
# 启动服务
python3 counter_service.py

# 在另一个终端中测试
curl http://localhost:8000/new
curl http://localhost:8000/query
curl http://localhost:8000/empty
```