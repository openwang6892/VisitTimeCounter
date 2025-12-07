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

## 环境变量配置（可选）

- `DATABASE_URL` - PostgreSQL数据库连接URL（如果留空则使用SQLite数据库）
  - 如果您在Render上创建了PostgreSQL数据库，可以将其连接到您的Web服务
  - 这样可以确保数据在服务重启后仍然保留

## 重要说明

- 服务会监听Render提供的PORT环境变量
- 计数器数据优先存储在PostgreSQL数据库中（通过DATABASE_URL环境变量配置）
- 如果没有配置PostgreSQL，将回退到SQLite数据库（数据在Render上可能不会持久保存）
- 在Render上部署时，建议配置PostgreSQL数据库以确保完全的数据持久化

## API端点

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

## 故障排除

- 如果部署失败，请检查Render日志中的错误信息
- 确保requirements.txt中的依赖项正确
- 如果使用PostgreSQL，请验证DATABASE_URL格式正确
- 检查端口是否从PORT环境变量获取