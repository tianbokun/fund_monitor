from flask import Flask, request, jsonify, render_template_string
import json
import os
from lib.fund_service import FundService

app = Flask(__name__)
fund_service = FundService()
DATA_FILE = "monitored_funds.json"

def load_funds():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_funds(funds):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(funds, f, ensure_ascii=False, indent=2)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>基金限购监控</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        .fund { border: 1px solid #ccc; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .orange { color: orange; }
        .green { color: green; }
        .red { color: red; }
        button { padding: 8px 15px; margin: 5px; cursor: pointer; }
        input { padding: 8px; margin: 5px; }
    </style>
</head>
<body>
    <h1>基金限购监控</h1>
    <div>
        <button onclick="loadFunds()">刷新</button>
        <button onclick="showAdd()">添加</button>
    </div>
    <div id="msg"></div>
    <div id="addForm" style="display:none; border: 2px solid #1976d2; padding: 20px; margin: 10px 0;">
        <h3>添加监控基金</h3>
        <p>输入6位基金代码</p>
        <input type="text" id="codeInput" placeholder="基金代码">
        <button onclick="addFund()">确定</button>
        <button onclick="hideAdd()">取消</button>
    </div>
    <div id="funds"></div>

    <script>
        function loadFunds() {
            fetch('/api/funds')
                .then(r => r.json())
                .then(data => {
                    let html = '';
                    data.forEach(f => {
                        html += `<div class="fund">
                            <b>${f.name}</b><br>
                            <span style="color:grey;font-size:12px">${f.code}</span><br>
                            <span class="${f.c}"><b>日限购: ${f.limit}</b></span><br>
                            <span class="${f.sc}">${f.status}</span>
                        </div>`;
                    });
                    document.getElementById('funds').innerHTML = html || '点击 添加 按钮添加基金';
                });
        }

        function showAdd() { document.getElementById('addForm').style.display = 'block'; }
        function hideAdd() { document.getElementById('addForm').style.display = 'none'; }

        function addFund() {
            const code = document.getElementById('codeInput').value.trim();
            if (!code) return;
            fetch('/api/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code})
            }).then(r => r.json()).then(data => {
                document.getElementById('msg').innerHTML = `<p style="color:${data.color}">${data.msg}</p>`;
                hideAdd();
                loadFunds();
            });
        }

        loadFunds();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/funds')
def api_funds():
    funds = load_funds()
    result = []
    for code in funds:
        info = fund_service.get_fund_limit(code)
        if info:
            limit = f"{info.daily_limit:,.0f}" if info.daily_limit and info.daily_limit < 1e12 else "无限额"
            c = "orange" if info.daily_limit and info.daily_limit < 1e12 else "green"
            sc = "red" if "暂停" in info.status else "green"
            result.append({"name": info.name, "code": info.code, "limit": limit, "status": info.status, "c": c, "sc": sc})
    return jsonify(result)

@app.route('/api/add', methods=['POST'])
def api_add():
    data = request.json
    code = data.get('code', '').strip()
    funds = load_funds()
    
    if code in funds:
        return jsonify({"msg": "已存在", "color": "orange"})
    
    info = fund_service.get_fund_limit(code)
    if info:
        funds.append(code)
        save_funds(funds)
        return jsonify({"msg": f"已添加: {info.name}", "color": "green"})
    else:
        return jsonify({"msg": "未找到", "color": "red"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8553, debug=False)
