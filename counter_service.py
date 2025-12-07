#!/usr/bin/env python3
"""
简单计数器服务
- 访问 /new 增加计数
- 访问 /query 查询总数
- 计数数据保存在PostgreSQL数据库中（优先），回退到SQLite
"""

import os
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# 从环境变量获取数据库URL
DATABASE_URL = os.environ.get('DATABASE_URL')

def _get_db_connection():
    """获取数据库连接 - 优先使用PostgreSQL，回退到SQLite"""
    if DATABASE_URL:
        try:
            # 尝试导入psycopg2
            import psycopg2
            # 使用PostgreSQL
            return psycopg2.connect(DATABASE_URL), 'postgres'
        except ImportError:
            print("psycopg2未安装，使用SQLite作为回退")
            DB_FILE = 'counter.db'
            return sqlite3.connect(DB_FILE), 'sqlite'
        except Exception as e:
            print(f"PostgreSQL连接失败，使用SQLite作为回退: {e}")
            DB_FILE = 'counter.db'
            return sqlite3.connect(DB_FILE), 'sqlite'
    else:
        # 使用SQLite
        DB_FILE = 'counter.db'
        return sqlite3.connect(DB_FILE), 'sqlite'

def init_db():
    """初始化数据库 - 优先使用PostgreSQL，回退到SQLite"""
    conn, db_type = _get_db_connection()
    try:
        if db_type == 'postgres':
            import psycopg2
            c = conn.cursor()
            # 创建计数表（如果不存在）
            c.execute('''CREATE TABLE IF NOT EXISTS counter
                         (id INTEGER PRIMARY KEY, count INTEGER DEFAULT 0)''')
            
            # 检查是否已有计数记录
            c.execute("SELECT count FROM counter WHERE id = 1")
            result = c.fetchone()
            if result is None:
                # 如果没有记录，创建初始记录
                c.execute("INSERT INTO counter (id, count) VALUES (1, 0)")
        else:  # SQLite
            c = conn.cursor()
            # 创建计数表（如果不存在）
            c.execute('''CREATE TABLE IF NOT EXISTS counter
                         (id INTEGER PRIMARY KEY, count INTEGER DEFAULT 0)''')
            
            # 检查是否已有计数记录
            c.execute("SELECT count FROM counter WHERE id = 1")
            result = c.fetchone()
            if result is None:
                # 如果没有记录，创建初始记录
                c.execute("INSERT INTO counter (id, count) VALUES (1, 0)")
        
        conn.commit()
    finally:
        conn.close()

def get_counter():
    """从数据库中读取计数 - 优先使用PostgreSQL，回退到SQLite"""
    conn, db_type = _get_db_connection()
    try:
        if db_type == 'postgres':
            import psycopg2
            c = conn.cursor()
            c.execute("SELECT count FROM counter WHERE id = 1")
            result = c.fetchone()
        else:  # SQLite
            c = conn.cursor()
            c.execute("SELECT count FROM counter WHERE id = 1")
            result = c.fetchone()
        return result[0] if result else 0
    finally:
        conn.close()

def save_counter(count):
    """将计数保存到数据库 - 优先使用PostgreSQL，回退到SQLite"""
    conn, db_type = _get_db_connection()
    try:
        if db_type == 'postgres':
            import psycopg2
            c = conn.cursor()
            c.execute("INSERT INTO counter (id, count) VALUES (1, %s) ON CONFLICT (id) DO UPDATE SET count = %s", (count, count))
        else:  # SQLite
            c = conn.cursor()
            c.execute("UPDATE counter SET count = ? WHERE id = 1", (count,))
            c.execute("INSERT OR REPLACE INTO counter (id, count) VALUES (1, ?)", (count,))
        conn.commit()
    finally:
        conn.close()

class CounterHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/new':
            # 增加计数
            current_count = get_counter()
            new_count = current_count + 1
            save_counter(new_count)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Connection', 'close')  # HTTP/1.1 连接管理
            self.end_headers()
            self.wfile.write(f"{new_count}".encode('utf-8'))
            
        elif self.path == '/query':
            # 查询总数
            current_count = get_counter()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Connection', 'close')  # HTTP/1.1 连接管理
            self.end_headers()
            self.wfile.write(f"{current_count}".encode('utf-8'))
            
        else:
            # 未找到路径
            self.send_response(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def log_message(self, format, *args):
        """重写日志方法以控制输出"""
        # 可以在这里自定义日志输出
        pass

def run_server(port=8000):
    """启动服务器"""
    # 初始化数据库
    init_db()
    
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, CounterHandler)
    print(f"服务器启动在端口 {port}")
    print(f"访问 /new 增加计数")
    print(f"访问 /query 查询总数")
    print("按 Ctrl+C 停止服务器")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        httpd.server_close()

if __name__ == '__main__':
    # Render会通过环境变量提供端口
    import os
    port = int(os.environ.get('PORT', 8000))
    run_server(port)

