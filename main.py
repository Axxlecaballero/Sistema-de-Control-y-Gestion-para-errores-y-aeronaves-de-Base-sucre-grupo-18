import flet as ft
from fleet_view import get_fleet_view
from reports_view import get_reports_view
from database import init_db

def main(page: ft.Page):
    # Inicializar base de datos
    init_db()
    # Configuración básica de la página
    page.title = "AERO-CONTROL: Gestión de Mantenimiento Aeronáutico"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 1200
    page.window.height = 900
    page.padding = 0
    page.bgcolor = "#0f172a"

    # Obtener las vistas
    view_mantenimiento = get_fleet_view(page)
    view_fallas = get_reports_view(page)

    # --- LÓGICA NAVEGACIÓN ---
    def on_nav_change(e):
        idx = e.control.selected_index
        view_mantenimiento.visible = (idx == 0)
        view_fallas.visible = (idx == 1)
        page.update()

    page.navigation_bar = ft.NavigationBar(
        bgcolor="#1e293b",
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.FLIGHT_TAKEOFF, label="Flota"),
            ft.NavigationBarDestination(icon=ft.Icons.REPORT_GMAILERRORRED, label="Reportes"),
        ],
        on_change=on_nav_change
    )

    page.add(ft.Row([view_mantenimiento, view_fallas], expand=True))

if __name__ == "__main__":
    ft.app(target=main)