import flet as ft

count = 0
msg = ft.Text("Hello Flet")

# Dialog container
dlg_container = ft.Container(
    visible=False,
    content=ft.Container(
        bgcolor="white",
        border=ft.Border.all(2, "blue"),
        border_radius=8,
        padding=20,
        content=ft.Column([
            ft.Text("Dialog is working!", size=18, weight="bold"),
            ft.Text("This is test content"),
            ft.Button("Close", on_click=lambda e: (setattr(dlg_container, 'visible', False), e.page.update())),
        ], spacing=10)
    ),
    width=400, height=300,
)

def add_clicked(e):
    global count
    count += 1
    msg.value = f"Count: {count}"
    msg.update()

def show_dlg(e):
    dlg_container.visible = True
    e.page.update()

def main(page: ft.Page):
    page.title = "Test App"
    page.add(
        msg,
        ft.Button("Click Me", on_click=add_clicked),
        ft.Button("Show Dialog", on_click=show_dlg),
        ft.Stack([
            dlg_container,
        ], expand=True),
    )

ft.app(target=main, port=8560, host="0.0.0.0", view=ft.AppView.WEB_BROWSER)
