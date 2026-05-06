import flet as ft
from flet import *
import time

class FundCard(UserControl):
    def __init__(self, fund_code, fund_name, daily_limit, status, on_delete=None):
        super().__init__()
        self.fund_code = fund_code
        self.fund_name = fund_name
        self.daily_limit = daily_limit
        self.status = status
        self.on_delete = on_delete
        
    def build(self):
        limit_text = f"{self.daily_limit:,.0f}" if self.daily_limit and self.daily_limit < 1e12 else "无限额"
        status_color = ft.colors.GREEN
        if self.status == "暂停申购":
            status_color = ft.colors.RED
        elif "限制" in self.status or "限额" in self.status:
            status_color = ft.colors.ORANGE
            
        return Card(
            content=Container(
                padding=15,
                content=Row([
                    Expanded(
                        Column([
                            Text(self.fund_name, weight=ft.FontWeight.BOLD, size=16),
                            Text(f"代码: {self.fund_code}", size=12, color=ft.colors.GREY_400),
                        ], spacing=2)
                    ),
                    Column([
                        Text("日限购额", size=11, color=ft.colors.GREY_400),
                        Text(limit_text, size=18, weight=ft.FontWeight.BOLD, 
                             color=ft.colors.ORANGE if self.daily_limit and self.daily_limit < 1e12 else ft.colors.GREEN),
                    ], horizontal_alignment=ft.CrossAxisAlignment.END),
                    Column([
                        Text("状态", size=11, color=ft.colors.GREY_400),
                        Container(
                            padding=padding.only(left=8, right=8, top=4, bottom=4),
                            bgcolor=status_color.with_opacity(0.2),
                            border_radius=border_radius.all(4),
                            content=Text(self.status, size=12, color=status_color, weight=ft.FontWeight.W500),
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.END),
                ], spacing=15),
            )
        )
        
    def update_fund(self, daily_limit, status):
        self.daily_limit = daily_limit
        self.status = status
        self.update()
        
    def delete(self):
        if self.on_delete:
            self.on_delete(self.fund_code)


class AddFundDialog(UserControl):
    def __init__(self, on_add, on_cancel):
        super().__init__()
        self.on_add = on_add
        self.on_cancel = on_cancel
        self.fund_code_input = TextField(label="基金代码", hint_text="例如: 000001", width=200)
        self.fund_name_input = TextField(label="基金简称(可选)", hint_text="会自动查询", width=200)
        
    def build(self):
        return AlertDialog(
            title=Text("添加监控基金"),
            content=Container(
                padding=20,
                content=Column([
                    self.fund_code_input,
                    self.fund_name_input,
                ], tight=True, spacing=20)
            ),
            actions=[
                TextButton("取消", on_click=self.on_cancel),
                FilledButton("添加", on_click=self._on_add_click),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
    def _on_add_click(self, e):
        code = self.fund_code_input.value.strip()
        if code:
            self.on_add(code)
            
    def clear(self):
        self.fund_code_input.value = ""
        self.fund_name_input.value = ""


class RefreshIndicator(UserControl):
    def __init__(self):
        super().__init__()
        self.progress = ProgressRing(width=20, height=20, stroke_width=2)
        
    def build(self):
        return Container(
            content=Row([
                self.progress,
                Text("正在更新...", size=14),
            ], spacing=10),
            padding=10,
        )