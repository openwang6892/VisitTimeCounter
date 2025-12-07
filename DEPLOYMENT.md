# 在Render上部署计数器服务

## 部署步骤

1. 将此仓库推送到GitHub
2. 登录Render账户
3. 点击"New +"按钮，选择"Web Service"
4. 连接您的GitHub账户并选择此仓库
5. Render会自动检测到这是一个Python项目

## 配置设置

- **Environment**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python counter_service.py`

## 重要说明

- 服务会监听Render提供的PORT环境变量
- 计数器数据优先存储在PostgreSQL数据库中（通过DATABASE_URL环境变量配置）
- 如果没有配置PostgreSQL，将回退到SQLite数据库
- 在Render上部署时，建议配置PostgreSQL数据库以确保完全的数据持久化

## API端点

- `GET /new` - 增加计数并返回新值
- `GET /query` - 查询当前总数

## 本地测试

在本地运行：
```bash
python counter_service.py
```

测试端点：
```bash
curl http://localhost:8000/new
curl http://localhost:8000/query
```