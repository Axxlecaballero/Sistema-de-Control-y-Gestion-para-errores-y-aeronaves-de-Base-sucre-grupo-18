import flet as ft

def main(page: ft.Page):
    # Configuración básica de la página
    page.title = "AERO-CONTROL: Gestión de Mantenimiento Aeronáutico"
    page.theme_mode = ft.ThemeMode.DARK  # Modo oscuro para un look más industrial y moderno
    page.window.width = 1200
    page.window.height = 900
    page.padding = 0
    page.bgcolor = "#0f172a"  # Color de fondo Slate muy oscuro

    # --- DATOS ESTÁTICOS DE PRUEBA (SIMULACIÓN) ---
    aviones = [
        {"sigla": "DA40-61442", "horas": 92, "estado": "Crítico"},
        {"sigla": "DA40-61557", "horas": 45, "estado": "Operativo"},
        {"sigla": "DA42-61651", "horas": 15, "estado": "Operativo"},
        {"sigla": "DA42-61653", "horas": 98, "estado": "Crítico"},
    ]

    fallas_data = [
        {"sigla": "YV-800", "reportante": "Juan Pérez", "falla": "Fuga Hidráulica", "status": "Pendiente"},
        {"sigla": "YV-520", "reportante": "Maria Lopez", "falla": "Falla Altímetro", "status": "Solucionado"},
        {"sigla": "YV-940", "reportante": "Carlos Ruíz", "falla": "Error de Sensor", "status": "En Revisión"},
    ]

    # --- COMPONENTES REUTILIZABLES ---

    def create_section_title(title, subtitle):
        """Crea un encabezado elegante para cada sección."""
        return ft.Column([
            ft.Text(title, size=32, weight="bold", color=ft.Colors.WHITE),
            ft.Text(subtitle, size=16, color=ft.Colors.BLUE_GREY_200),
            ft.Divider(height=30, color=ft.Colors.WHITE12)
        ], spacing=5)

    def aircraft_card(sigla, horas):
        """Genera una tarjeta visual para cada aeronave."""
        porcentaje = horas / 100
        es_critico = horas >= 90
        color_tema = ft.Colors.RED_ACCENT if es_critico else ft.Colors.CYAN_ACCENT

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.AIRPLANEMODE_ACTIVE, color=color_tema, size=30),
                    ft.Text(sigla, size=20, weight="bold"),
                    ft.Container(
                        content=ft.Text(
                            "INSPECCIÓN" if es_critico else "OK", 
                            size=10, 
                            weight="bold", 
                            color=ft.Colors.WHITE if es_critico else ft.Colors.BLACK
                        ),
                        bgcolor=color_tema,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                        border_radius=5
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Text(f"Horas de Vuelo: {horas} / 100 hr", size=14, color=ft.Colors.BLUE_GREY_100),
                ft.ProgressBar(value=porcentaje, color=color_tema, bgcolor=ft.Colors.WHITE10, height=8),
                
                ft.Row([
                    ft.ElevatedButton(
                        "Sumar Horas", 
                        icon=ft.Icons.ADD, 
                        style=ft.ButtonStyle(color=color_tema),
                        on_click=lambda _: print(f"Sumar horas a {sigla}")
                    ),
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=15),
            padding=20,
            bgcolor="#1e293b",
            border_radius=15,
            border=ft.Border.all(1, ft.Colors.WHITE10),
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK26)
        )

    # --- VISTA 1: GESTIÓN DE FLOTA Y MANTENIMIENTO ---
    grid_aviones = ft.ResponsiveRow(
        controls=[ft.Column([aircraft_card(a["sigla"], a["horas"])], col={"sm": 12, "md": 6, "lg": 4}) for a in aviones],
        spacing=20
    )

    view_mantenimiento = ft.Container(
        content=ft.Column([
            create_section_title("Gestión de Flota", "Control de horas permitidas y alertas de inspección"),
            ft.Container(
                content=ft.Row([
                    ft.TextField(label="Nueva Sigla", hint_text="Ej: YV-101", expand=True, border_color=ft.Colors.BLUE_GREY_700),
                    ft.TextField(label="Horas Iniciales", value="0", width=150, border_color=ft.Colors.BLUE_GREY_700),
                    ft.ElevatedButton(
                        "Registrar Avión", 
                        icon=ft.Icons.ADD, 
                        bgcolor=ft.Colors.CYAN_ACCENT, 
                        color=ft.Colors.BLACK
                    ),
                ], spacing=15),
                margin=ft.margin.only(bottom=20)
            ),
            grid_aviones
        ], scroll=ft.ScrollMode.ADAPTIVE),
        padding=40,
        expand=True
    )

    # --- VISTA 2: REPORTE DE FALLAS Y SOLUCIONES ---
    view_fallas = ft.Container(
        content=ft.Column([
            create_section_title("Reportes de Fallas", "Registro de incidencias técnicas y soluciones aplicadas"),
            
            # Formulario de Registro
            ft.Card(
                content=ft.Container(
                    padding=30,
                    bgcolor="#1e293b",
                    content=ft.Column([
                        ft.Text("Nuevo Reporte de Falla", size=18, weight="bold", color=ft.Colors.CYAN_ACCENT),
                        ft.Row([
                            ft.TextField(label="Sigla del Avión", expand=1, border_color=ft.Colors.BLUE_GREY_700),
                            ft.TextField(label="Nombre del Reportante", expand=2, border_color=ft.Colors.BLUE_GREY_700),
                        ]),
                        ft.TextField(label="Título de la Falla", border_color=ft.Colors.BLUE_GREY_700),
                        ft.TextField(label="Descripción técnica", multiline=True, min_lines=3, border_color=ft.Colors.BLUE_GREY_700),
                        ft.Row([
                            ft.ElevatedButton("Reportar Solución", icon=ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.GREEN_400),
                            ft.ElevatedButton("Enviar Reporte de Falla", icon=ft.Icons.SEND, bgcolor=ft.Colors.CYAN_ACCENT, color=ft.Colors.BLACK),
                        ], alignment=ft.MainAxisAlignment.END, spacing=10)
                    ], spacing=15)
                )
            ),
            
            ft.Text("Historial de Incidencias", size=20, weight="bold", margin=ft.margin.only(top=30)),
            ft.DataTable(
                heading_row_color=ft.Colors.WHITE10,
                columns=[
                    ft.DataColumn(ft.Text("Aeronave")),
                    ft.DataColumn(ft.Text("Falla Detectada")),
                    ft.DataColumn(ft.Text("Técnico")),
                    ft.DataColumn(ft.Text("Estado")),
                ],
                rows=[
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
                ],
                expand=True
            )
        ], scroll=ft.ScrollMode.ADAPTIVE),
        padding=40,
        expand=True,
        visible=False
    )

    # --- VISTA 3: ESTADÍSTICAS Y GRÁFICAS ---
    # Simulación de gráfica personalizada con Contenedores (100% compatible)
    def chart_bar(label, value, color, max_val=15):
        height_px = (value / max_val) * 300  # Proporción para la altura
        return ft.Column([
            ft.Container(
                width=40,
                height=height_px,
                bgcolor=color,
                border_radius=ft.border_radius.only(top_left=5, top_right=5),
                tooltip=f"{value} incidencias"
            ),
            ft.Text(label, size=12, color=ft.Colors.BLUE_GREY_200)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.END)

    chart_simulado = ft.Container(
        content=ft.Row([
            chart_bar("Avionica", 12, ft.Colors.CYAN),
            chart_bar("Plataforma", 8, ft.Colors.BLUE),
            chart_bar("Mat compuesto", 15, ft.Colors.AMBER),
            chart_bar("Motores", 10, ft.Colors.RED),
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, vertical_alignment=ft.CrossAxisAlignment.END),
        height=350,
        padding=20,
        bgcolor="#1e293b",
        border_radius=15,
        border=ft.Border.all(1, ft.Colors.WHITE10),
    )

    view_stats = ft.Container(
        content=ft.Column([
            create_section_title("Análisis de Confiabilidad", "Estadísticas anuales de fallas y aeronaves críticas"),
            
            ft.Row([
                ft.Card(
                    expand=1,
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Falla más frecuente", color=ft.Colors.BLUE_GREY_200),
                            ft.Text("Mat compuesto", size=24, weight="bold", color=ft.Colors.CYAN_ACCENT),
                            ft.Text("15 incidencias este año", size=12)
                        ])
                    )
                ),
                ft.Card(
                    expand=1,
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Aeronave Crítica", color=ft.Colors.BLUE_GREY_200),
                            ft.Text("YV-940", size=24, weight="bold", color=ft.Colors.RED_ACCENT),
                            ft.Text("8 reportes totales", size=12)
                        ])
                    )
                ),
            ], spacing=20),
            
            ft.Text("Distribución de Fallas por Sistema", size=20, weight="bold", margin=ft.margin.only(top=30)),
            ft.Container(
                content=chart_simulado,
                margin=ft.margin.only(top=10)
            )
        ], scroll=ft.ScrollMode.ADAPTIVE),
        padding=40,
        expand=True,
        visible=False
    )

    # --- LÓGICA DE NAVEGACIÓN ---
    def on_nav_change(e):
        idx = e.control.selected_index
        view_mantenimiento.visible = (idx == 0)
        view_fallas.visible = (idx == 1)
        view_stats.visible = (idx == 2)
        page.update()

    page.navigation_bar = ft.NavigationBar(
        bgcolor="#1e293b",
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.FLIGHT_TAKEOFF, label="Flota"),
            ft.NavigationBarDestination(icon=ft.Icons.REPORT_GMAILERRORRED, label="Reportes"),
            ft.NavigationBarDestination(icon=ft.Icons.INSERT_CHART_OUTLINED, label="Estadísticas"),
        ],
        on_change=on_nav_change
    )

    # Agregar todo a la página
    page.add(
        ft.Row([
            view_mantenimiento,
            view_fallas,
            view_stats
        ], expand=True)
    )

# Lanzar la aplicación
ft.run(main)