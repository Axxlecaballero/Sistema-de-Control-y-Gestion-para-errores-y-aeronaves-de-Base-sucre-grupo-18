import flet as ft
from components import create_section_title, aircraft_card
from database import obtener_aeronaves, registrar_aeronave, sumar_horas_vuelo, realizar_inspeccion

def get_fleet_view(page: ft.Page):
    # --- LÓGICA DE SUMAR HORAS ---
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
        dialogo_inspeccion.open = False
        page.update()

    def confirmar_suma(e):
        nonlocal selected_sigla
        try:
            nuevas_horas = float(input_horas_nuevas.value)
            sumar_horas_vuelo(selected_sigla, nuevas_horas)
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

    # --- LÓGICA DE INSPECCIÓN ---
    input_tecnico = ft.TextField(label="Técnico Responsable", border_color=ft.Colors.BLUE_GREY_700)

    def confirmar_inspeccion(e):
        nonlocal selected_sigla
        if not input_tecnico.value:
            input_tecnico.error_text = "Requerido"
            page.update()
            return
            
        if realizar_inspeccion(selected_sigla, input_tecnico.value):
            actualizar_grid()
            cerrar_dialogo(e)
            page.snack_bar = ft.SnackBar(ft.Text(f"Inspección registrada para {selected_sigla}"))
            page.snack_bar.open = True
            page.update()

    dialogo_inspeccion = ft.AlertDialog(
        modal=True,
        title=ft.Text("Finalizar Inspección"),
        content=ft.Column([
            ft.Text("¿Confirma que se ha realizado la inspección técnica?", color=ft.Colors.BLUE_GREY_200),
            ft.Text("Esto incrementará el límite de la próxima inspección.", size=12, color=ft.Colors.AMBER_ACCENT),
            input_tecnico,
        ], tight=True, spacing=20),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo),
            ft.Button("Confirmar Inspección", bgcolor=ft.Colors.GREEN_400, color=ft.Colors.BLACK, on_click=confirmar_inspeccion),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialogo_sumar)
    page.overlay.append(dialogo_inspeccion)

    def abrir_dialogo_sumar(sigla):
        nonlocal selected_sigla
        selected_sigla = sigla
        dialogo_sumar.title = ft.Text(f"Añadir Horas: {sigla}")
        input_horas_nuevas.value = "" 
        input_horas_nuevas.error_text = None
        dialogo_sumar.open = True
        page.update()

    def abrir_dialogo_inspeccion(sigla):
        nonlocal selected_sigla
        selected_sigla = sigla
        dialogo_inspeccion.title = ft.Text(f"Inspección: {sigla}")
        input_tecnico.value = ""
        input_tecnico.error_text = None
        dialogo_inspeccion.open = True
        page.update()

    def actualizar_grid():
        aviones = obtener_aeronaves()
        grid_aviones.controls = [
            ft.Column([aircraft_card(
                a["sigla"], 
                a["horas"], 
                a["max_horas"], 
                a["prox_inspeccion"], 
                abrir_dialogo_sumar,
                abrir_dialogo_inspeccion
            )], col={"sm": 12, "md": 6, "lg": 4}) 
            for a in aviones
        ]
        page.update()

    # Carga inicial de aviones
    aviones_db = obtener_aeronaves()
    grid_aviones = ft.ResponsiveRow(
        controls=[ft.Column([aircraft_card(
            a["sigla"], 
            a["horas"], 
            a["max_horas"], 
            a["prox_inspeccion"], 
            abrir_dialogo_sumar,
            abrir_dialogo_inspeccion
        )], col={"sm": 12, "md": 6, "lg": 4}) for a in aviones_db],
        spacing=20
    )

    input_nueva_sigla = ft.TextField(label="Nueva Sigla", hint_text="Ej: YV-101", expand=True, border_color=ft.Colors.BLUE_GREY_700, dense=True)
    input_horas_ini = ft.TextField(label="Horas Iniciales", value="0", width=150, border_color=ft.Colors.BLUE_GREY_700, dense=True)

    def registrar_avion_click(e):
        if not input_nueva_sigla.value:
            input_nueva_sigla.error_text = "Campo requerido"
            page.update()
            return
        
        try:
            horas = float(input_horas_ini.value)
            if registrar_aeronave(input_nueva_sigla.value, horas):
                input_nueva_sigla.value = ""
                input_horas_ini.value = "0"
                input_nueva_sigla.error_text = None
                actualizar_grid()
                page.snack_bar = ft.SnackBar(ft.Text("Aeronave registrada con éxito"))
                page.snack_bar.open = True
            else:
                input_nueva_sigla.error_text = "La sigla ya existe"
            page.update()
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
                        on_click=registrar_avion_click
                    ),
                ], spacing=15),
                margin=ft.Margin.only(bottom=20)
            ),
            grid_aviones
        ], scroll=ft.ScrollMode.ADAPTIVE),
        padding=40,
        expand=True
    )

    return view_mantenimiento
