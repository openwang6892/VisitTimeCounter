# 计数器服务

一个简单的HTTP计数器服务，具有以下功能：

- 访问 `/new` 增加计数
- 访问 `/query` 查询总数
- 计数数据保存在本地文件中

## 本地使用方法

1. 运行服务：
   ```bash
   python3 counter_service.py
   ```

2. 服务启动后，您可以通过以下方式使用：
   - `GET /new` - 增加计数并返回新值
   - `GET /query` - 查询当前总数

## 示例

```bash
# 增加计数
curl http://localhost:8000/new

# 查询总数
curl http://localhost:8000/query
```

## Render部署

此项目已配置为可在Render上部署：

1. 将此项目连接到GitHub仓库
2. 在Render上创建Web Service
3. 使用以下设置：
   - 环境: Python
   - 构建命令: `pip install -r requirements.txt`
   - 启动命令: `python counter_service.py`

## 数据持久化

计数数据会优先保存在PostgreSQL数据库中（通过DATABASE_URL环境变量指定），如果没有配置PostgreSQL则会回退到SQLite数据库 (`counter.db`)。在Render上部署时，配置PostgreSQL数据库可确保数据的完全持久化。