import flet as ft
import os
import sys
from fleet_view import get_fleet_view
from reports_view import get_reports_view
from piezas_view import get_piezas_view
from estadisticas_view import get_estadisticas_view
from database import init_db

# Ruta base: funciona tanto en desarrollo como empaquetado con PyInstaller
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def main(page: ft.Page):
    # Inicializar base de datos
    init_db()
    page.title = "AERO-CONTROL GEANº18"
    page.window.icon = os.path.join(BASE_PATH, "logo.ico")
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 1200
    page.window.height = 900
    page.padding = 0
    page.bgcolor = "#0f172a"

    # Obtener las vistas
    view_mantenimiento = get_fleet_view(page)
    view_piezas = get_piezas_view(page)
    view_fallas = get_reports_view(page)
    view_estadisticas = get_estadisticas_view(page)

    # --- LÓGICA NAVEGACIÓN ---
    def on_nav_change(e):
        idx = e.control.selected_index
        view_mantenimiento.visible = (idx == 0)
        view_piezas.visible = (idx == 1)
        view_fallas.visible = (idx == 2)
        view_estadisticas.visible = (idx == 3)
        
        if idx == 1 and hasattr(view_piezas, 'refresh_data'):
            view_piezas.refresh_data()
        
        if idx == 2 and hasattr(view_fallas, 'refresh_data'):
            view_fallas.refresh_data()

        if idx == 3 and hasattr(view_estadisticas, 'refresh_data'):
            view_estadisticas.refresh_data()
            
        page.update()

    page.navigation_bar = ft.NavigationBar(
        bgcolor="#1e293b",
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.FLIGHT_TAKEOFF, label="Flota"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Piezas"),
            ft.NavigationBarDestination(icon=ft.Icons.REPORT_GMAILERRORRED, label="Reportes"),
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART, label="Estadísticas"),
        ],
        on_change=on_nav_change
    )

    page.add(ft.Row([view_mantenimiento, view_piezas, view_fallas, view_estadisticas], expand=True))

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")