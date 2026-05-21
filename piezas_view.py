import flet as ft
from components import create_section_title, pieza_card
from database import obtener_aeronaves, obtener_piezas_por_sigla, registrar_pieza, intercambiar_pieza_db

def get_piezas_view(page: ft.Page):
    selected_sigla = None

    def on_aeronave_change(e):
        nonlocal selected_sigla
        selected_sigla = dropdown_aeronaves.value
        cargar_piezas(selected_sigla)

    dropdown_aeronaves = ft.Dropdown(
        label="Seleccionar Aeronave",
        border_color=ft.Colors.BLUE_GREY_700,
        expand=1,
        on_select=on_aeronave_change
    )

    input_nombre_pieza = ft.TextField(label="Nombre Pieza", border_color=ft.Colors.BLUE_GREY_700, dense=True, expand=1)
    input_pn = ft.TextField(label="Número Parte", border_color=ft.Colors.BLUE_GREY_700, dense=True, expand=1)
    input_sn = ft.TextField(label="Número Serie", border_color=ft.Colors.BLUE_GREY_700, dense=True, expand=1)
    input_fabricante = ft.TextField(label="Fabricante", border_color=ft.Colors.BLUE_GREY_700, dense=True, expand=1)
    input_horas_pieza = ft.TextField(label="Horas Iniciales", value="0", border_color=ft.Colors.BLUE_GREY_700, dense=True, expand=1)
    
    lista_piezas_row = ft.ResponsiveRow(spacing=20)

    # Título dinámico para el formulario de registro
    titulo_registro = ft.Text("Registrar Nueva Pieza", size=18, weight="bold", color=ft.Colors.CYAN_ACCENT)

    # --- LÓGICA DE INTERCAMBIO DE PIEZAS ---
    dropdown_inter_origen = ft.Dropdown(
        label="Aeronave Origen",
        border_color=ft.Colors.BLUE_GREY_700,
        expand=True
    )

    dropdown_inter_pieza = ft.Dropdown(
        label="Pieza a Intercambiar",
        border_color=ft.Colors.BLUE_GREY_700,
        expand=True
    )

    dropdown_inter_destino = ft.Dropdown(
        label="Aeronave Destino",
        border_color=ft.Colors.BLUE_GREY_700,
        expand=True
    )

    def on_origen_select(e):
        sigla_origen = dropdown_inter_origen.value
        if not sigla_origen:
            return
        
        # Cargar piezas asociadas al avión de origen
        piezas = obtener_piezas_por_sigla(sigla_origen)
        dropdown_inter_pieza.options = [
            ft.dropdown.Option(
                key=str(p["id_pieza"]), 
                text=f"{p['nombre_pieza']} (S/N: {p['numero_serie']}) - {p['horas_pieza']} hr"
            ) for p in piezas
        ]
        dropdown_inter_pieza.value = None
        
        # Cargar aviones destino excluyendo el origen
        aviones = obtener_aeronaves()
        dropdown_inter_destino.options = [
            ft.dropdown.Option(a["sigla"]) for a in aviones if a["sigla"] != sigla_origen
        ]
        dropdown_inter_destino.value = None
        
        page.update()

    dropdown_inter_origen.on_select = on_origen_select

    def abrir_dialogo_intercambio(e):
        aviones = obtener_aeronaves()
        dropdown_inter_origen.options = [ft.dropdown.Option(a["sigla"]) for a in aviones]
        dropdown_inter_origen.value = selected_sigla
        
        dropdown_inter_pieza.options = []
        dropdown_inter_pieza.value = None
        
        dropdown_inter_destino.options = []
        dropdown_inter_destino.value = None
        
        if selected_sigla:
            on_origen_select(None)
            
        dialogo_intercambio.open = True
        page.update()

    def confirmar_intercambio(e):
        id_pieza = dropdown_inter_pieza.value
        sigla_destino = dropdown_inter_destino.value
        
        if not id_pieza:
            page.snack_bar = ft.SnackBar(ft.Text("Seleccione una pieza para intercambiar"), bgcolor=ft.Colors.RED_400)
            page.snack_bar.open = True
            page.update()
            return
            
        if not sigla_destino:
            page.snack_bar = ft.SnackBar(ft.Text("Seleccione una aeronave destino"), bgcolor=ft.Colors.RED_400)
            page.snack_bar.open = True
            page.update()
            return
            
        success, msg = intercambiar_pieza_db(int(id_pieza), sigla_destino)
        if success:
            dialogo_intercambio.open = False
            cargar_piezas(selected_sigla)
            page.snack_bar = ft.SnackBar(ft.Text(msg))
            page.snack_bar.open = True
        else:
            page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.RED_400)
            page.snack_bar.open = True
        page.update()

    dialogo_intercambio = ft.AlertDialog(
        modal=True,
        title=ft.Text("Intercambiar Pieza entre Aeronaves"),
        content=ft.Container(
            width=500,
            content=ft.Column([
                ft.Text("Transfiere un componente a otra aeronave manteniendo intacto su historial de horas de vuelo.", color=ft.Colors.BLUE_GREY_200, size=14),
                ft.Divider(height=10, color=ft.Colors.WHITE_12),
                dropdown_inter_origen,
                dropdown_inter_pieza,
                dropdown_inter_destino,
            ], tight=True, spacing=15)
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: (setattr(dialogo_intercambio, 'open', False), page.update())),
            ft.ElevatedButton("Intercambiar", bgcolor=ft.Colors.CYAN_ACCENT, color=ft.Colors.BLACK, on_click=confirmar_intercambio),
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    page.overlay.append(dialogo_intercambio)

    def cargar_dropdown_aeronaves():
        nonlocal selected_sigla
        aviones = obtener_aeronaves()
        dropdown_aeronaves.options = [ft.dropdown.Option(a["sigla"]) for a in aviones]
        if aviones:
            if not selected_sigla or not any(a["sigla"] == selected_sigla for a in aviones):
                selected_sigla = aviones[0]["sigla"]
            dropdown_aeronaves.value = selected_sigla
            cargar_piezas(selected_sigla)
        else:
            selected_sigla = None
            dropdown_aeronaves.value = None
            cargar_piezas(None)

    def registrar_nueva_pieza(e):
        if not selected_sigla:
            page.snack_bar = ft.SnackBar(ft.Text("Primero seleccione una aeronave"), bgcolor=ft.Colors.RED_400)
            page.snack_bar.open = True
            page.update()
            return
            
        if not input_nombre_pieza.value:
            input_nombre_pieza.error_text = "Requerido"
            page.update()
            return
        try:
            horas = float(input_horas_pieza.value)
        except ValueError:
            input_horas_pieza.error_text = "Inválido"
            page.update()
            return

        success, msg = registrar_pieza(
            selected_sigla,
            input_nombre_pieza.value,
            input_pn.value,
            input_sn.value,
            input_fabricante.value,
            horas
        )
        if success:
            input_nombre_pieza.value = ""
            input_pn.value = ""
            input_sn.value = ""
            input_fabricante.value = ""
            input_horas_pieza.value = "0"
            input_nombre_pieza.error_text = None
            input_horas_pieza.error_text = None
            cargar_piezas(selected_sigla)
            page.snack_bar = ft.SnackBar(ft.Text(msg))
            page.snack_bar.open = True
        else:
            page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.RED_400)
            page.snack_bar.open = True
        page.update()

    def cargar_piezas(sigla):
        nonlocal selected_sigla
        selected_sigla = sigla
        
        # Sincronizar el valor visual del dropdown con el estado de Python
        dropdown_aeronaves.value = sigla

        if not sigla:
            registro_card.visible = False
            piezas_section.visible = False
            placeholder_card.visible = True
            page.update()
            return

        # Si hay sigla seleccionada, habilitamos las secciones y actualizamos el título
        registro_card.visible = True
        piezas_section.visible = True
        placeholder_card.visible = False
        titulo_registro.value = f"Registrar Nueva Pieza para {sigla}"

        piezas = obtener_piezas_por_sigla(sigla)
        lista_piezas_row.controls.clear()
        if not piezas:
            lista_piezas_row.controls.append(
                ft.Text(f"No hay piezas registradas para la aeronave {sigla}.", color=ft.Colors.BLUE_GREY_200)
            )
        else:
            for p in piezas:
                lista_piezas_row.controls.append(
                    ft.Column([pieza_card(p)], col={"sm": 12, "md": 6, "lg": 4})
                )
        page.update()

    # Cards y secciones dinámicas
    registro_card = ft.Card(
        content=ft.Container(
            padding=20, bgcolor="#1e293b",
            content=ft.Column([
                titulo_registro,
                ft.Row([input_nombre_pieza, input_pn, input_sn], spacing=10),
                ft.Row([
                    input_fabricante, 
                    input_horas_pieza, 
                    ft.ElevatedButton("Añadir Pieza", icon=ft.Icons.ADD, bgcolor=ft.Colors.CYAN_ACCENT, color=ft.Colors.BLACK, on_click=registrar_nueva_pieza)
                ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=15)
        ),
        margin=ft.Margin.only(top=10, bottom=20),
        visible=False
    )

    piezas_section = ft.Column([
        ft.Text("Piezas Instaladas", size=20, weight="bold"),
        lista_piezas_row
    ], visible=False)

    placeholder_card = ft.Card(
        content=ft.Container(
            padding=40, bgcolor="#1e293b",
            content=ft.Column([
                ft.Icon(ft.Icons.AIRPLANEMODE_INACTIVE, size=50, color=ft.Colors.BLUE_GREY_400),
                ft.Text("Seleccione una aeronave en el menú superior para ver y registrar sus piezas.", size=16, color=ft.Colors.BLUE_GREY_200, text_align=ft.TextAlign.CENTER),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ),
        margin=ft.Margin.only(top=10, bottom=20),
        visible=True
    )

    # Initial load of dropdown
    cargar_dropdown_aeronaves()

    # Method to refresh data when view becomes visible
    def refresh_data():
        cargar_dropdown_aeronaves()
        if selected_sigla:
            aviones = obtener_aeronaves()
            if any(a["sigla"] == selected_sigla for a in aviones):
                cargar_piezas(selected_sigla)
            else:
                dropdown_aeronaves.value = None
                cargar_piezas(None)
        else:
            cargar_piezas(None)
        page.update()

    view_piezas = ft.Container(
        content=ft.Column([
            create_section_title("Gestión de Piezas", "Control de horas y estado de componentes de aeronaves"),
            ft.Row([
                dropdown_aeronaves, 
                ft.IconButton(icon=ft.Icons.REFRESH, on_click=lambda _: refresh_data(), tooltip="Actualizar Aeronaves"),
                ft.ElevatedButton("Intercambiar Pieza", icon=ft.Icons.SWAP_HORIZ, bgcolor="#475569", color=ft.Colors.WHITE, on_click=abrir_dialogo_intercambio)
            ], alignment=ft.MainAxisAlignment.START),
            placeholder_card,
            registro_card,
            piezas_section
        ], scroll=ft.ScrollMode.ADAPTIVE),
        padding=40,
        expand=True,
        visible=False
    )
    
    # Attach the refresh method so it can be called from main.py
    view_piezas.refresh_data = refresh_data

    return view_piezas
