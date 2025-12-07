#!/usr/bin/env python3
import os
import sqlite3
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

DATABASE_URL = os.environ.get('DATABASE_URL')

def _get_db_connection():
    if DATABASE_URL:
        try:
            import psycopg2
            return psycopg2.connect(DATABASE_URL), 'postgres'
        except ImportError:
            pass  # psycopg2 not installed, fall back to SQLite
        except Exception:
            pass  # Connection failed, fall back to SQLite
    # Use SQLite as fallback
    DB_FILE = 'counter.db'
    return sqlite3.connect(DB_FILE), 'sqlite'

def init_db():
    conn, db_type = _get_db_connection()
    try:
        c = conn.cursor()
        if db_type == 'postgres':
            import psycopg2
            c.execute('''CREATE TABLE IF NOT EXISTS counter
                         (id INTEGER PRIMARY KEY, count INTEGER DEFAULT 0)''')
            c.execute('''CREATE TABLE IF NOT EXISTS records
                         (ts INTEGER PRIMARY KEY, count INTEGER DEFAULT 1)''')
            c.execute("SELECT count FROM counter WHERE id = 1")
            result = c.fetchone()
            if result is None:
                c.execute("INSERT INTO counter (id, count) VALUES (1, 0)")
        else:
            c.execute('''CREATE TABLE IF NOT EXISTS counter
                         (id INTEGER PRIMARY KEY, count INTEGER DEFAULT 0)''')
            c.execute('''CREATE TABLE IF NOT EXISTS records
                         (ts INTEGER PRIMARY KEY, count INTEGER DEFAULT 1)''')
            c.execute("SELECT count FROM counter WHERE id = 1")
            result = c.fetchone()
            if result is None:
                c.execute("INSERT INTO counter (id, count) VALUES (1, 0)")
        conn.commit()
    finally:
        conn.close()

def get_counter():
    conn, db_type = _get_db_connection()
    try:
        c = conn.cursor()
        if db_type == 'postgres':
            import psycopg2
            c.execute("SELECT count FROM counter WHERE id = 1")
        else:
            c.execute("SELECT count FROM counter WHERE id = 1")
        result = c.fetchone()
        return result[0] if result else 0
    finally:
        conn.close()

def save_counter(count):
    conn, db_type = _get_db_connection()
    try:
        c = conn.cursor()
        if db_type == 'postgres':
            import psycopg2
            c.execute("INSERT INTO counter (id, count) VALUES (1, %s) ON CONFLICT (id) DO UPDATE SET count = EXCLUDED.count", (count,))
        else:
            c.execute("INSERT OR REPLACE INTO counter (id, count) VALUES (1, ?)", (count,))
        conn.commit()
    finally:
        conn.close()

def add_record():
    conn, db_type = _get_db_connection()
    try:
        ts = int(time.time())
        c = conn.cursor()
        if db_type == 'postgres':
            import psycopg2
            c.execute("INSERT INTO records (ts, count) VALUES (%s, 1) ON CONFLICT (ts) DO UPDATE SET count = records.count + 1", (ts,))
        else:
            c.execute("INSERT OR IGNORE INTO records (ts, count) VALUES (?, 1)", (ts,))
            c.execute("UPDATE records SET count = count + 1 WHERE ts = ?", (ts,))
        conn.commit()
    finally:
        conn.close()

def query_range(start, end):
    conn, db_type = _get_db_connection()
    try:
        if db_type == 'postgres':
            import psycopg2
            c = conn.cursor()
            c.execute("SELECT SUM(count) FROM records WHERE ts >= %s AND ts <= %s", (start, end))
            result = c.fetchone()
        else:
            c = conn.cursor()
            c.execute("SELECT SUM(count) FROM records WHERE ts >= ? AND ts <= ?", (start, end))
            result = c.fetchone()
        return result[0] if result[0] else 0
    finally:
        conn.close()

class CounterHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/new'):
            import urllib.parse
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            increase_count = 1
            if 'num' in query_params:
                try:
                    increase_count = int(query_params['num'][0])
                except ValueError:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/plain; charset=utf-8')
                    self.send_header('Connection', 'close')
                    self.end_headers()
                    self.wfile.write(b"Invalid num parameter")
                    return
            if 'to' in query_params:
                try:
                    target_value = int(query_params['to'][0])
                    current_count = get_counter()
                    if target_value > current_count:
                        increase_count = target_value - current_count
                    else:
                        self.send_response(400)
                        self.send_header('Content-type', 'text/plain; charset=utf-8')
                        self.send_header('Connection', 'close')
                        self.end_headers()
                        self.wfile.write(b"Cannot assign to the value you specified")
                        return
                except ValueError:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/plain; charset=utf-8')
                    self.send_header('Connection', 'close')
                    self.end_headers()
                    self.wfile.write(b"Invalid to parameter")
                    return
            current_count = get_counter()
            new_count = current_count + increase_count
            save_counter(new_count)
            for _ in range(increase_count):
                add_record()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(f"{new_count}".encode('utf-8'))
        elif self.path.startswith('/query'):
            import urllib.parse
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            now = int(time.time())
            today_start = now - now % 86400
            week_start = now - 86400 * 6
            month_start = now - 86400 * 30
            if 'range' in query_params:
                rng = query_params['range'][0]
                if rng == 'today':
                    count = query_range(today_start, now)
                elif rng == 'week':
                    count = query_range(week_start, now)
                elif rng == 'month':
                    count = query_range(month_start, now)
                else:
                    count = get_counter()
            else:
                count = get_counter()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(f"{count}".encode('utf-8'))
        elif self.path.startswith('/empty'):
            import urllib.parse
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            current_count = get_counter()
            if 'num' in query_params:
                try:
                    reduce_num = int(query_params['num'][0])
                    new_count = max(0, current_count - reduce_num)
                    save_counter(new_count)
                    response = f"{new_count}"
                except ValueError:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/plain; charset=utf-8')
                    self.send_header('Connection', 'close')
                    self.end_headers()
                    self.wfile.write(b"Invalid num parameter")
                    return
            elif 'to' in query_params:
                try:
                    target_value = int(query_params['to'][0])
                    if target_value < current_count:
                        save_counter(target_value)
                        response = f"{target_value}"
                    else:
                        response = "Cannot assign to the value you specified"
                except ValueError:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/plain; charset=utf-8')
                    self.send_header('Connection', 'close')
                    self.end_headers()
                    self.wfile.write(b"Invalid to parameter")
                    return
            else:
                save_counter(0)
                response = "0"
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(b"Not Found")
    def log_message(self, format, *args):
        pass

def run_server(port=8000):
    init_db()
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, CounterHandler)
    print(f"服务器启动在端口 {port}")
    print(f"访问 /new 增加计数")
    print(f"访问 /query 查询总数")
    print(f"访问 /empty 清空")
    print("按 Ctrl+C 停止服务器")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        httpd.server_close()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    run_server(port)