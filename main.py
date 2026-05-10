import flet as ft

def main(page: ft.Page):
    # Configuración básica de la página
    page.title = "AERO-CONTROL: Gestión de Mantenimiento Aeronáutico"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 1200
    page.window.height = 900
    page.padding = 0
    page.bgcolor = "#0f172a"

    # --- DATOS ESTÁTICOS DE PRUEBA ---
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

    # --- LÓGICA DE VENTANA EMERGENTE (DIALOG) ---
    
    input_horas_nuevas = ft.TextField(
        label="Cantidad de horas", 
        hint_text="Ej: 5.5",
        prefix_icon=ft.Icons.TIMER,
        border_color=ft.Colors.BLUE_GREY_700,
        keyboard_type=ft.KeyboardType.NUMBER
    )

    selected_sigla = None # Sigla del avión que se está editando

    def cerrar_dialogo(e):
        dialogo_sumar.open = False
        page.update()

    def confirmar_suma(e):
        nonlocal selected_sigla
        try:
            nuevas_horas = float(input_horas_nuevas.value)
            for a in aviones:
                if a["sigla"] == selected_sigla:
                    a["horas"] = round(a["horas"] + nuevas_horas, 2)
                    break
            actualizar_grid()
            cerrar_dialogo(e)
            page.snack_bar = ft.SnackBar(ft.Text(f"Horas añadidas a {selected_sigla}"))
            page.snack_bar.open = True
            page.update()
        except ValueError:
            input_horas_nuevas.error_text = "Ingrese un número válido"
            page.update()

    dialogo_sumar = ft.AlertDialog(
        modal=True,
        title=ft.Text("Registrar Vuelo"),
        content=ft.Column([
            ft.Text("Ingrese las horas de vuelo a añadir a esta aeronave:", color=ft.Colors.BLUE_GREY_200),
            input_horas_nuevas,
        ], tight=True, spacing=20),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo),
            ft.Button(
                "Confirmar", 
                bgcolor=ft.Colors.CYAN_ACCENT, 
                color=ft.Colors.BLACK, 
                on_click=confirmar_suma
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo_sumar) # Se añade una sola vez al inicio

    def abrir_dialogo_sumar(sigla):
        nonlocal selected_sigla
        selected_sigla = sigla
        dialogo_sumar.title = ft.Text(f"Añadir Horas: {sigla}")
        input_horas_nuevas.value = "" 
        input_horas_nuevas.error_text = None
        dialogo_sumar.open = True
        page.update()

    # --- COMPONENTES REUTILIZABLES ---

    def create_section_title(title, subtitle):
        return ft.Column([
            ft.Text(title, size=32, weight="bold", color=ft.Colors.WHITE),
            ft.Text(subtitle, size=16, color=ft.Colors.BLUE_GREY_200),
            ft.Divider(height=30, color=ft.Colors.WHITE_12)
        ], spacing=5)

    def aircraft_card(sigla, horas):
        # --- LÓGICA DE PRÓRROGA Y ESTADOS ---
        limite_base = 100
        prorroga = 10
        limite_total = limite_base + prorroga
        
        if horas >= limite_total:
            estado = "VENCIDO"
            color_tema = ft.Colors.RED_ACCENT
            porcentaje = 1.0
        elif horas >= limite_base:
            estado = "EN PRÓRROGA"
            color_tema = ft.Colors.RED_400
            porcentaje = horas / limite_total
        elif horas >= 90:
            estado = "CRÍTICO"
            color_tema = ft.Colors.ORANGE_400
            porcentaje = horas / limite_base
        else:
            estado = "OPERATIVO"
            color_tema = ft.Colors.CYAN_ACCENT
            porcentaje = horas / limite_base

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.AIRPLANEMODE_ACTIVE, color=color_tema, size=30),
                    ft.Text(sigla, size=20, weight="bold"),
                    ft.Container(
                        content=ft.Text(
                            estado, 
                            size=10, weight="bold", 
                            color=ft.Colors.BLACK if color_tema != ft.Colors.RED_ACCENT else ft.Colors.WHITE
                        ),
                        bgcolor=color_tema,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                        border_radius=5
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Text(
                    f"Horas: {horas} / {limite_base} " + (f"(+{prorroga} hr)" if horas >= limite_base else "hr"), 
                    size=14, color=ft.Colors.BLUE_GREY_100
                ),
                ft.ProgressBar(value=porcentaje, color=color_tema, bgcolor=ft.Colors.WHITE_10, height=8),
                
                ft.Row([
                    ft.Button(
                        "Sumar Horas", 
                        icon=ft.Icons.ADD, 
                        style=ft.ButtonStyle(color=color_tema),
                        on_click=lambda _: abrir_dialogo_sumar(sigla) # Llamada a la ventana emergente
                    ),
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=15),
            padding=20,
            bgcolor="#1e293b",
            border_radius=15,
            border=ft.Border.all(1, ft.Colors.WHITE_10),
        )

    # --- VISTAS ---
    # --- LÓGICA DE ACTUALIZACIÓN ---
    def actualizar_grid():
        grid_aviones.controls = [
            ft.Column([aircraft_card(a["sigla"], a["horas"])], col={"sm": 12, "md": 6, "lg": 4}) 
            for a in aviones
        ]
        page.update()

    # --- VISTAS ---
    grid_aviones = ft.ResponsiveRow(
        controls=[ft.Column([aircraft_card(a["sigla"], a["horas"])], col={"sm": 12, "md": 6, "lg": 4}) for a in aviones],
        spacing=20
    )

    input_nueva_sigla = ft.TextField(label="Nueva Sigla", hint_text="Ej: YV-101", expand=True, border_color=ft.Colors.BLUE_GREY_700, dense=True)
    input_horas_ini = ft.TextField(label="Horas Iniciales", value="0", width=150, border_color=ft.Colors.BLUE_GREY_700, dense=True)

    def registrar_avion(e):
        if not input_nueva_sigla.value:
            input_nueva_sigla.error_text = "Campo requerido"
            page.update()
            return
        
        try:
            horas = float(input_horas_ini.value)
            aviones.append({"sigla": input_nueva_sigla.value, "horas": horas})
            input_nueva_sigla.value = ""
            input_horas_ini.value = "0"
            input_nueva_sigla.error_text = None
            actualizar_grid()
        except ValueError:
            input_horas_ini.error_text = "Número inválido"
            page.update()

    view_mantenimiento = ft.Container(
        content=ft.Column([
            create_section_title("Gestión de Flota", "Control de horas permitidas y alertas de inspección"),
            ft.Container(
                content=ft.Row([
                    input_nueva_sigla,
                    input_horas_ini,
                    ft.Button(
                        "Registrar Avión", 
                        icon=ft.Icons.ADD, 
                        bgcolor=ft.Colors.CYAN_ACCENT, 
                        color=ft.Colors.BLACK,
                        height=40,
                        on_click=registrar_avion
                    ),
                ], spacing=15),
                margin=ft.Margin.only(bottom=20)
            ),
            grid_aviones
        ], scroll=ft.ScrollMode.ADAPTIVE),
        padding=40,
        expand=True
    )

    # --- VISTA 2: REPORTE DE FALLAS Y SOLUCIONES ---
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

ft.app(target=main)