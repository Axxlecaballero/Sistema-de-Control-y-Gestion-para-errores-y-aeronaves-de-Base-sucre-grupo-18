import flet as ft
from components import create_section_title
from database import obtener_aeronaves, obtener_piezas_por_sigla, registrar_falla_db, obtener_fallas_db, actualizar_falla_db

def get_reports_view(page: ft.Page):
    
    # --- FUNCIÓN DE NOTIFICACIÓN POP-UP ---
    def mostrar_popup(titulo, mensaje, color=ft.Colors.CYAN_ACCENT):
        def cerrar(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text(titulo, color=color, weight="bold"),
            content=ft.Text(mensaje),
            actions=[ft.TextButton("Entendido", on_click=cerrar)]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # --- CAMPOS DE ENTRADA (Estilizados uniformemente) ---
    dd_sigla_nuevo = ft.Dropdown(label="Sigla del Avión", expand=1, border_color=ft.Colors.BLUE_GREY_700)
    in_tecnico = ft.TextField(label="Nombre del Reportante", expand=1, border_color=ft.Colors.BLUE_GREY_700)
    in_falla = ft.TextField(label="Título de la Falla", expand=1, border_color=ft.Colors.BLUE_GREY_700)
    in_desc = ft.TextField(label="Descripción técnica", multiline=True, min_lines=3, expand=1, border_color=ft.Colors.BLUE_GREY_700)

    in_inspector = ft.TextField(label="Inspector Responsable", expand=1, border_color=ft.Colors.BLUE_GREY_700)
    in_titulo_falla_info = ft.TextField(label="Falla Detectada", expand=1, border_color=ft.Colors.BLUE_GREY_700)
    dd_estado = ft.Dropdown(label="Estado", options=[ft.dropdown.Option("Pendiente"), ft.dropdown.Option("Solucionado")], value="Solucionado", expand=1)
    dd_piezas_avion = ft.Dropdown(label="Pieza Afectada", expand=1, border_color=ft.Colors.BLUE_GREY_700)
    in_razon_falla = ft.TextField(label="Razón de la Falla / Acción Tomada", multiline=True, min_lines=3, expand=1, border_color=ft.Colors.BLUE_GREY_700)

    # --- CARGA FIEL DE PIEZAS ---
    def cargar_piezas_en_dropdown(sigla_aeronave):
        piezas = obtener_piezas_por_sigla(sigla_aeronave)
        dd_piezas_avion.options.clear()
        
        if not piezas:
            dd_piezas_avion.options.append(
                ft.dropdown.Option(text="No hay piezas registradas en esta aeronave", disabled=True)
            )
        else:
            for p in piezas:
                dd_piezas_avion.options.append(
                    ft.dropdown.Option(text=p["nombre_pieza"])
                )
        
        dd_piezas_avion.value = None
        dd_piezas_avion.update()

    # --- EVENTO DE SELECCIÓN NATIVO (on_select) ---
    def al_seleccionar_reporte(e):
        if not dd_reportes_abiertos.value: 
            return
        
        try:
            cadena_completa = dd_reportes_abiertos.value
            partes = cadena_completa.split(" - ")
            
            if len(partes) >= 2:
                sigla_limpia = partes[0].strip()
                falla_limpia = partes[1].strip()

                in_titulo_falla_info.value = falla_limpia
                in_titulo_falla_info.update()
                
                cargar_piezas_en_dropdown(sigla_limpia)
        except Exception as ex:
            print(f"Error en al_seleccionar_reporte: {ex}")

    # Inicialización del Dropdown principal ocupando todo el ancho de su fila
    dd_reportes_abiertos = ft.Dropdown(
        label="Seleccionar Reporte Pendiente",
        border_color=ft.Colors.CYAN_ACCENT,
        expand=1,
        on_select=al_seleccionar_reporte
    )

    # --- ACCIONES DE BOTONES ---
    def enviar_reporte_click(e):
        if not all([dd_sigla_nuevo.value, in_tecnico.value, in_falla.value, in_desc.value]):
            mostrar_popup("Atención", "Por favor, llene todos los campos del reporte.", ft.Colors.ORANGE_400)
            return
        
        if registrar_falla_db(dd_sigla_nuevo.value, in_tecnico.value, in_falla.value, in_desc.value):
            mostrar_popup("Éxito", "Reporte registrado correctamente.", ft.Colors.GREEN_400)
            in_falla.value = ""; in_desc.value = ""; in_tecnico.value = ""; dd_sigla_nuevo.value = None
            actualizar_tabla()
        
    def guardar_solucion_click(e):
        if not all([dd_reportes_abiertos.value, in_inspector.value, dd_piezas_avion.value, in_razon_falla.value]):
            mostrar_popup("Atención", "Debe completar la solución y elegir una pieza afectada.", ft.Colors.ORANGE_400)
            return

        cadena_completa = dd_reportes_abiertos.value
        partes = cadena_completa.split(" - ")
        
        if len(partes) < 2:
            mostrar_popup("Error", "El formato del reporte seleccionado es incorrecto.", ft.Colors.RED_400)
            return
            
        sigla_limpia = partes[0].strip()
        titulo_original = partes[1].strip()

        exito = actualizar_falla_db(
            sigla_limpia,
            titulo_original,
            in_inspector.value,
            in_titulo_falla_info.value,
            dd_estado.value,
            dd_piezas_avion.value,
            in_razon_falla.value
        )

        if exito:
            mostrar_popup("Completado", "La inspección se guardó correctamente.", ft.Colors.GREEN_400)
            in_inspector.value = ""
            in_razon_falla.value = ""
            in_titulo_falla_info.value = ""
            dd_piezas_avion.value = None
            dd_reportes_abiertos.value = None
            cambiar_vista(False)
            actualizar_tabla()
        else:
            mostrar_popup("Error", "No se pudo actualizar la falla en la base de datos.", ft.Colors.RED_400)

    # --- MÉTODOS DE RENDERIZADO AUXILIAR ---
    def cargar_aviones():
        aviones = obtener_aeronaves()
        dd_sigla_nuevo.options = [ft.dropdown.Option(a["sigla"]) for a in aviones]

    def actualizar_tabla():
        fallas = obtener_fallas_db()
        tabla_fallas.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(f["sigla"])),
                ft.DataCell(ft.Text(f["falla"])),
                ft.DataCell(ft.Text(f["reportante"])),
                ft.DataCell(ft.Container(
                    content=ft.Text(f["status"], size=12, weight="bold", color=ft.Colors.BLACK),
                    bgcolor=ft.Colors.CYAN_ACCENT if f["status"] == "Solucionado" else ft.Colors.AMBER_ACCENT,
                    padding=ft.Padding.symmetric(horizontal=10, vertical=4), border_radius=10
                )),
            ]) for f in fallas
        ]
        page.update()

    def cambiar_vista(mostrar_solucion):
        if mostrar_solucion:
            fallas = obtener_fallas_db()
            dd_reportes_abiertos.options = [
                ft.dropdown.Option(f"{f['sigla']} - {f['falla']}") for f in fallas if f["status"] == "Pendiente"
            ]
            form_nuevo.visible = False
            form_solucion.visible = True
        else:
            form_nuevo.visible = True
            form_solucion.visible = False
        page.update()

    # --- FORMULARIO 1: NUEVO REPORTE (Estructura en Grilla) ---
    form_nuevo = ft.Column([
        ft.Text("Nuevo Reporte de Falla", size=18, weight="bold", color=ft.Colors.CYAN_ACCENT),
        ft.Row([dd_sigla_nuevo, in_tecnico], spacing=20),
        ft.Row([in_falla], spacing=20),
        ft.Row([in_desc], spacing=20),
        ft.Row([
            ft.Button("Gestionar Soluciones", icon=ft.Icons.SETTINGS, on_click=lambda _: cambiar_vista(True)),
            ft.Button("Enviar Reporte", icon=ft.Icons.SEND, bgcolor=ft.Colors.CYAN_ACCENT, color=ft.Colors.BLACK, on_click=enviar_reporte_click),
        ], alignment=ft.MainAxisAlignment.END, spacing=15)
    ], spacing=15)

    # --- FORMULARIO 2: REPORTAR SOLUCIÓN (Estructura en Grilla Avanzada) ---
    form_solucion = ft.Column([
        ft.Text("Reportar Solución", size=18, weight="bold", color=ft.Colors.GREEN_400),
        ft.Row([dd_reportes_abiertos], spacing=20),
        ft.Row([in_inspector, in_titulo_falla_info], spacing=20),
        ft.Row([dd_estado, dd_piezas_avion], spacing=20),
        ft.Row([in_razon_falla], spacing=20),
        ft.Row([
            ft.TextButton("Volver", on_click=lambda _: cambiar_vista(False)),
            ft.Button("Guardar Solución", icon=ft.Icons.CHECK, bgcolor=ft.Colors.GREEN_400, color=ft.Colors.BLACK, on_click=guardar_solucion_click),
        ], alignment=ft.MainAxisAlignment.END, spacing=15)
    ], spacing=15, visible=False)

    tabla_fallas = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Aeronave")), 
            ft.DataColumn(ft.Text("Falla")), 
            ft.DataColumn(ft.Text("Técnico")), 
            ft.DataColumn(ft.Text("Estado"))
        ], 
        rows=[]
    )

    cargar_aviones()
    actualizar_tabla()

    return ft.Container(
        content=ft.Column([
            create_section_title("Gestión de Reportes", "Control de incidencias y soluciones técnicas"),
            ft.Card(content=ft.Container(padding=30, bgcolor="#1e293b", content=ft.Column([form_nuevo, form_solucion]))),
            ft.Text("Historial de Incidencias", size=20, weight="bold", margin=ft.Margin.only(top=20)),
            tabla_fallas
        ], scroll=ft.ScrollMode.ADAPTIVE),
        padding=40, expand=True, visible=False
    )