import flet as ft
import json
import os
from lib.fund_service import FundService

DATA_FILE = "monitored_funds.json"

fund_service = FundService()
monitored_funds = []

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            monitored_funds = json.load(f)
    except:
        monitored_funds = []

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(monitored_funds, f, ensure_ascii=False, indent=2)

def main(page: ft.Page):
    page.title = "基金限购监控"
    page.scroll = "auto"

    msg = ft.Text("", color="green")
    code_input = ft.TextField(label="基金代码", width=250)
    progress_bar = ft.ProgressBar(width=200, visible=False)
    progress_text = ft.Text("", size=12, visible=False)

    # 主容器 - 固定高度以启用滚动
    content_col = ft.Column(scroll="auto", spacing=10)

    def update_fund_list(funds_dict):
        content_col.controls.clear()
        if not monitored_funds:
            content_col.controls.append(ft.Text("点击 添加 按钮添加基金"))
        else:
            # 表头行
            header = ft.Row([
                ft.Text("基金代码", weight="bold", width=100),
                ft.Text("基金名称", weight="bold", expand=True),
                ft.Text("日限购额", weight="bold", width=120),
                ft.Text("申购状态", weight="bold", width=100),
            ], spacing=10)
            content_col.controls.append(header)
            content_col.controls.append(ft.Divider())

            # 数据行
            for code in monitored_funds:
                info = funds_dict.get(code)
                if info:
                    limit = f"{info.daily_limit:,.0f}" if info.daily_limit and info.daily_limit < 1e12 else "无限额"
                    limit_color = "orange" if info.daily_limit and info.daily_limit < 1e12 else "green"
                    status_color = "red" if "暂停" in info.status else "green"
                    row = ft.Row([
                        ft.Text(info.code, width=100),
                        ft.Text(info.name, expand=True),
                        ft.Text(limit, color=limit_color, weight="bold", width=120),
                        ft.Text(info.status, color=status_color, width=100),
                    ], spacing=10)
                    content_col.controls.append(row)
        page.update()

    def load_funds(e=None):
        if not monitored_funds:
            update_fund_list({})
            return
        progress_bar.visible = True
        progress_text.value = "正在加载数据..."
        progress_text.visible = True
        page.update()
        funds_dict = fund_service.get_funds_batch(monitored_funds)
        progress_bar.visible = False
        progress_text.visible = False
        update_fund_list(funds_dict)

    def hide_add(e=None):
        add_row.visible = False
        page.update()

    def on_confirm_add(e):
        code = code_input.value.strip()
        if not code:
            hide_add()
            return
        if code in monitored_funds:
            msg.value = "已存在"
            msg.color = "orange"
            page.update()
            code_input.value = ""
            hide_add()
            return
        progress_bar.visible = True
        progress_text.value = "正在验证基金代码..."
        progress_text.visible = True
        page.update()
        all_codes = monitored_funds + [code]
        funds_dict = fund_service.get_funds_batch(all_codes)
        info = funds_dict.get(code)
        progress_bar.visible = False
        progress_text.visible = False
        if info:
            monitored_funds.append(code)
            save_data()
            msg.value = f"已添加: {info.name}"
            msg.color = "green"
            update_fund_list(funds_dict)
        else:
            msg.value = "未找到"
            msg.color = "red"
            page.update()
        code_input.value = ""
        add_row.visible = False
        page.update()

    def on_refresh(e):
        load_funds()
        msg.value = "已刷新"
        msg.color = "green"
        page.update()

    def on_add(e):
        add_row.visible = True
        page.update()

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
        ft.Container(width=10),
        progress_bar,
        ft.Container(width=10),
        progress_text,
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
                    content=content_col,
                    height=500,
                ),
            ], spacing=10)
        )
    )
    load_funds()

if __name__ == "__main__":
    ft.run(main, host="0.0.0.0", port=8550, view=ft.AppView.WEB_BROWSER)