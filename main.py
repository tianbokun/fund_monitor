import flet as ft
import json
import os
from lib.fund_service import FundService

DATA_FILE = "monitored_funds.json"

fund_service = FundService()
monitored_funds = []

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            monitored_funds = json.load(f)
    except:
        monitored_funds = []

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(monitored_funds, f, ensure_ascii=False, indent=2)

def main(page: ft.Page):
    page.title = "基金限购监控"
    
    msg = ft.Text("", color="green")
    fund_list = ft.Column(scroll="auto", expand=True, spacing=10)
    code_input = ft.TextField(label="基金代码", width=250)
    
    def load_funds():
        fund_list.controls.clear()
        for code in monitored_funds:
            info = fund_service.get_fund_limit(code)
            if info:
                limit = f"{info.daily_limit:,.0f}" if info.daily_limit and info.daily_limit < 1e12 else "无限额"
                c = "orange" if info.daily_limit and info.daily_limit < 1e12 else "green"
                sc = "red" if "暂停" in info.status else "green"
                fund_list.controls.append(
                    ft.Container(
                        padding=10, margin=5,
                        border=ft.Border.all(1, "#ccc"),
                        border_radius=5,
                        content=ft.Column([
                            ft.Text(info.name, weight="bold"),
                            ft.Text(info.code, size=12, color="grey"),
                            ft.Text(f"日限购: {limit}", color=c, weight="bold"),
                            ft.Text(info.status, color=sc),
                        ], spacing=2)
                    )
                )
        page.update()
    
    def hide_add(e=None):
        add_row.visible = False
        page.update()
    
    def on_confirm_add(e):
        code = code_input.value.strip()
        if code:
            if code in monitored_funds:
                msg.value = "已存在"
                msg.color = "orange"
            else:
                info = fund_service.get_fund_limit(code)
                if info:
                    monitored_funds.append(code)
                    save_data()
                    load_funds()
                    msg.value = f"已添加: {info.name}"
                    msg.color = "green"
                else:
                    msg.value = "未找到"
                    msg.color = "red"
            code_input.value = ""
        hide_add()
    
    def on_refresh(e):
        load_funds()
        msg.value = "已刷新"
        msg.color = "green"
        page.update()
    
    def on_add(e):
        add_row.visible = True
        page.update()
    
    # 添加区域（直接在页面上显示/隐藏）
    add_row = ft.Row([
        code_input,
        ft.Button("确定", on_click=on_confirm_add),
        ft.Button("取消", on_click=hide_add),
    ], visible=False)
    
    toolbar = ft.Row([
        ft.Text("基金限购监控", size=22, weight="bold"),
        ft.Container(width=20),
        ft.Button("刷新", on_click=on_refresh, width=70),
        ft.Button("添加", on_click=on_add, width=70),
    ])
    
    page.add(
        ft.Container(
            padding=15,
            content=ft.Column([
                toolbar,
                msg,
                add_row,
                ft.Divider(),
                ft.Container(
                    content=fund_list if monitored_funds else ft.Text("点击 添加 按钮添加基金"),
                    expand=True,
                ),
            ], spacing=10)
        )
    )
    
    load_funds()

if __name__ == "__main__":
    ft.app(main, host="0.0.0.0", port=8553)
