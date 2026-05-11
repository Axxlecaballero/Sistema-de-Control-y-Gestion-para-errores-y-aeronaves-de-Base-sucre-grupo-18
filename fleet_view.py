import flet as ft
from components import create_section_title, aircraft_card
from data import aviones

def get_fleet_view(page: ft.Page):
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
    page.overlay.append(dialogo_sumar)

    def abrir_dialogo_sumar(sigla):
        nonlocal selected_sigla
        selected_sigla = sigla
        dialogo_sumar.title = ft.Text(f"Añadir Horas: {sigla}")
        input_horas_nuevas.value = "" 
        input_horas_nuevas.error_text = None
        dialogo_sumar.open = True
        page.update()

    def actualizar_grid():
        grid_aviones.controls = [
            ft.Column([aircraft_card(a["sigla"], a["horas"], abrir_dialogo_sumar)], col={"sm": 12, "md": 6, "lg": 4}) 
            for a in aviones
        ]
        page.update()

    grid_aviones = ft.ResponsiveRow(
        controls=[ft.Column([aircraft_card(a["sigla"], a["horas"], abrir_dialogo_sumar)], col={"sm": 12, "md": 6, "lg": 4}) for a in aviones],
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

    return view_mantenimiento
