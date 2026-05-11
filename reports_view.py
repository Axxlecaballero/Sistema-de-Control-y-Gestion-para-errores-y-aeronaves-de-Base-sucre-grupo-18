import flet as ft
from components import create_section_title
from data import fallas_data

def get_reports_view(page: ft.Page):
    # --- CAMPOS REPORTE ---
    in_sigla = ft.TextField(label="Sigla del Avión", expand=1, border_color=ft.Colors.BLUE_GREY_700)
    in_tecnico = ft.TextField(label="Nombre del Reportante", expand=2, border_color=ft.Colors.BLUE_GREY_700)
    in_falla = ft.TextField(label="Título de la Falla", border_color=ft.Colors.BLUE_GREY_700)
    in_desc = ft.TextField(label="Descripción técnica", multiline=True, min_lines=3, border_color=ft.Colors.BLUE_GREY_700)

    tabla_fallas = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Aeronave")),
            ft.DataColumn(ft.Text("Falla")),
            ft.DataColumn(ft.Text("Técnico")),
            ft.DataColumn(ft.Text("Estado")),
        ],
        rows=[]
    )

    def actualizar_tabla():
        tabla_fallas.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(f["sigla"])),
                ft.DataCell(ft.Text(f["falla"])),
                ft.DataCell(ft.Text(f["reportante"])),
                ft.DataCell(ft.Container(
                    content=ft.Text(f["status"], size=12, weight="bold", color=ft.Colors.BLACK),
                    bgcolor=ft.Colors.CYAN_ACCENT if f["status"] == "Solucionado" else ft.Colors.AMBER_ACCENT,
                    padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                    border_radius=10
                )),
            ]) for f in fallas_data
        ]
        page.update()

    def enviar_reporte(e):
        if not in_sigla.value or not in_falla.value:
            return
        fallas_data.append({
            "sigla": in_sigla.value,
            "reportante": in_tecnico.value,
            "falla": in_falla.value,
            "status": "Pendiente"
        })
        in_sigla.value = ""
        in_tecnico.value = ""
        in_falla.value = ""
        in_desc.value = ""
        actualizar_tabla()

    actualizar_tabla() # Carga inicial

    view_fallas = ft.Container(
        content=ft.Column([
            create_section_title("Reportes de Fallas", "Registro de incidencias técnicas y soluciones aplicadas"),
            ft.Card(
                content=ft.Container(
                    padding=30, bgcolor="#1e293b",
                    content=ft.Column([
                        ft.Text("Nuevo Reporte de Falla", size=18, weight="bold", color=ft.Colors.CYAN_ACCENT),
                        ft.Row([in_sigla, in_tecnico]),
                        in_falla,
                        in_desc,
                        ft.Row([
                            ft.Button("Reportar Solución", icon=ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.GREEN_400),
                            ft.Button("Enviar Reporte", icon=ft.Icons.SEND, bgcolor=ft.Colors.CYAN_ACCENT, color=ft.Colors.BLACK, on_click=enviar_reporte),
                        ], alignment=ft.MainAxisAlignment.END, spacing=10)
                    ], spacing=15)
                )
            ),
            ft.Text("Historial de Incidencias", size=20, weight="bold", margin=ft.Margin.only(top=30)),
            tabla_fallas
        ], scroll=ft.ScrollMode.ADAPTIVE),
        padding=40, expand=True, visible=False
    )

    return view_fallas
