# VisitTimesCounter - 访问次数计数器

## 项目概述

VisitTimesCounter 是一个轻量级的HTTP计数器服务，用于跟踪网站或API的访问次数。该服务支持多种计数操作，并提供灵活的数据持久化选项。

## 主要功能

1. **计数操作**：
   - `/new` - 增加计数
   - `/query` - 查询总数
   - `/empty` - 清空计数

2. **高级功能**：
   - 支持批量增加计数（`/new?num=5`）
   - 支持设置特定值（`/new?to=100`）
   - 支持按时间范围查询（今日/本周/本月）
   - 支持减少计数（`/empty?num=5`）
   - 支持设置特定值（`/empty?to=10`）

3. **数据持久化**：
   - 优先使用PostgreSQL（通过DATABASE_URL环境变量配置）
   - 备选使用SQLite数据库（`counter.db`）
   - 记录每次访问的时间戳

## 技术特点

- 使用Python标准库实现，无需额外依赖
- 支持PostgreSQL和SQLite两种数据库
   - PostgreSQL用于生产环境（数据持久）
   - SQLite用于开发和测试
- 支持Render等平台的部署
- 自动处理数据库连接和错误恢复

## 部署方式

### 本地运行
```bash
python3 counter_service.py
```

### Render部署
- 使用Python环境
- 构建命令：`pip install -r requirements.txt`
- 启动命令：`python counter_service.py`

## API端点示例

- `GET /new` - 增加计数1次
- `GET /new?num=5` - 增加计数5次
- `GET /new?to=100` - 设置计数到100
- `GET /query` - 查询总访问量
- `GET /query?range=today` - 查询今日访问量
- `GET /empty` - 清空计数
- `GET /empty?num=5` - 减少5次计数

## 项目文件

- `counter_service.py` - 主服务文件
- `requirements.txt` - 依赖文件
- `README.md` - 基本使用说明
- `DEPLOYMENT.md` - 部署说明
- `render.yaml` - Render部署配置
- `counter.db` - SQLite数据库文件