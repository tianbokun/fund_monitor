#!/usr/bin/env python3
import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys

DATA_FILE = "monitored_funds.json"
SEARCH_HISTORY_FILE = "search_history.json"
ADD_HISTORY_FILE = "add_history.json"

def load_json(file):
    if os.path.exists(file):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

html_template = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>基金限购监控 - 历史记录</title>
    <style>
        body { font-family: Arial; max-width: 1200px; margin: 50px auto; padding: 20px; }
        h1, h2 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ccc; padding: 10px; text-align: left; }
        th { background-color: #f5f5f5; }
        .empty { color: #999; font-style: italic; }
        button { padding: 8px 15px; margin: 5px; cursor: pointer; background: #1976d2; color: white; border: none; border-radius: 4px; }
        button:hover { background: #1565c0; }
        .tabs { margin: 20px 0; }
        .tab-btn { padding: 10px 20px; margin-right: 5px; cursor: pointer; background: #f5f5f5; border: 1px solid #ccc; }
        .tab-btn.active { background: #1976d2; color: white; }
        .tab-content { display: none; margin-top: 20px; }
        .tab-content.active { display: block; }
    </style>
    <script>
        function showTab(tab) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tab).classList.add('active');
            event.target.classList.add('active');
        }
    </script>
</head>
<body>
    <h1>基金限购监控 - 历史记录</h1>
    
    <div class="tabs">
        <button class="tab-btn active" onclick="showTab('search')">搜索历史</button>
        <button class="tab-btn" onclick="showTab('add')">添加历史</button>
        <button class="tab-btn" onclick="showTab('funds')">监控基金</button>
    </div>
    
    <div id="search" class="tab-content active">
        <h2>搜索历史</h2>
        {search_table}
        <form method="post" action="/clear_search">
            <button type="submit" onclick="return confirm('确定清空搜索历史？')">清空搜索历史</button>
        </form>
    </div>
    
    <div id="add" class="tab-content">
        <h2>添加历史</h2>
        {add_table}
        <form method="post" action="/clear_add">
            <button type="submit" onclick="return confirm('确定清空添加历史？')">清空添加历史</button>
        </form>
    </div>
    
    <div id="funds" class="tab-content">
        <h2>监控基金列表</h2>
        {funds_table}
    </div>
</body>
</html>
'''

class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = html_template.format(
                search_table=search_table,
                add_table=add_table,
                funds_table=funds_table
            )
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/clear_search':
            save_json(SEARCH_HISTORY_FILE, [])
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        elif self.path == '/clear_add':
            save_json(ADD_HISTORY_FILE, [])
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        pass  # 静默日志

if __name__ == '__main__':
    port = 8502
    server = HTTPServer(('0.0.0.0', port), RequestHandler)
    print(f'服务已启动: http://{sys.argv[1] if len(sys.argv) > 1 else "172.28.79.193"}:{port}')
    print('按 Ctrl+C 停止服务')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n服务已停止')
