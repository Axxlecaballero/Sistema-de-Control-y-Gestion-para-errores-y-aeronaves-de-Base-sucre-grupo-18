import flet as ft
from datetime import datetime
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

    # --- CAMPOS DE ENTRADA ---
    dd_sigla_nuevo = ft.Dropdown(label="Sigla del Avión", expand=1, border_color=ft.Colors.BLUE_GREY_700)
    in_tecnico = ft.TextField(label="Nombre del Reportante", expand=1, border_color=ft.Colors.BLUE_GREY_700)
    in_falla = ft.TextField(label="Título de la Falla", expand=1, border_color=ft.Colors.BLUE_GREY_700)
    in_desc = ft.TextField(label="Descripción técnica", multiline=True, min_lines=3, expand=1, border_color=ft.Colors.BLUE_GREY_700)

    # Variable para almacenar la fecha seleccionada en formato YYYY-MM-DD
    fecha_seleccionada_str = datetime.now().strftime("%Y-%m-%d")

    # Texto visible que muestra la fecha seleccionada actualmente (por defecto hoy)
    txt_fecha_visible = ft.TextField(
        label="Fecha del Reporte", 
        value=fecha_seleccionada_str, 
        read_only=True, 
        expand=True,
        border_color=ft.Colors.BLUE_GREY_700
    )

    # Función que se ejecuta cuando el usuario escoge una fecha en el calendario
    def al_cambiar_calendario(e):
        nonlocal fecha_seleccionada_str
        if picker_calendario.value:
            fecha_seleccionada_str = picker_calendario.value.strftime("%Y-%m-%d")
            txt_fecha_visible.value = fecha_seleccionada_str
            txt_fecha_visible.update()

    # Componente DatePicker nativo de Flet
    picker_calendario = ft.DatePicker(
        on_change=al_cambiar_calendario,
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2030, 12, 31),
    )
    page.overlay.append(picker_calendario) # Se registra en el overlay de la página

    in_inspector = ft.TextField(label="Inspector Responsable", expand=1, border_color=ft.Colors.BLUE_GREY_700)
    in_titulo_falla_info = ft.TextField(label="Falla Detectada", expand=1, border_color=ft.Colors.BLUE_GREY_700)
    dd_estado = ft.Dropdown(label="Estado", options=[ft.dropdown.Option("Pendiente"), ft.dropdown.Option("Solucionado")], value="Solucionado", expand=1)
    dd_piezas_avion = ft.Dropdown(label="Pieza Afectada", expand=1, border_color=ft.Colors.BLUE_GREY_700)
    in_razon_falla = ft.TextField(label="Razón de la Falla / Acción Tomada", multiline=True, min_lines=3, expand=1, border_color=ft.Colors.BLUE_GREY_700)

    # ---  LISTA LOCAL Y CAMPOS DE FILTROS ---
    fallas_locales = []
    pagina_actual = 0
    REGISTROS_POR_PAGINA = 10

    btn_anterior = ft.IconButton(
        icon=ft.Icons.ARROW_BACK_IOS_NEW,
        icon_color=ft.Colors.CYAN_ACCENT,
        disabled=True,
        on_click=lambda e: cambiar_pagina(-1)
    )
    btn_siguiente = ft.IconButton(
        icon=ft.Icons.ARROW_FORWARD_IOS,
        icon_color=ft.Colors.CYAN_ACCENT,
        disabled=True,
        on_click=lambda e: cambiar_pagina(1)
    )
    txt_info_pagina = ft.Text("Página 1", color=ft.Colors.BLUE_GREY_300, size=14, weight="bold")

    filtro_aeronave = ft.Dropdown(label="Aeronave", width=150, border_color=ft.Colors.BLUE_GREY_700, on_select=lambda e: aplicar_filtros())
    filtro_estado = ft.Dropdown(
        label="Estado", 
        width=150, 
        border_color=ft.Colors.BLUE_GREY_700,
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Pendiente"),
            ft.dropdown.Option("Solucionado")
        ],
        value="Todos",
        on_select=lambda e: aplicar_filtros()
    )
    filtro_mes = ft.Dropdown(
        label="Mes", 
        width=150, 
        border_color=ft.Colors.BLUE_GREY_700,
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("01", "Enero"),
            ft.dropdown.Option("02", "Febrero"),
            ft.dropdown.Option("03", "Marzo"),
            ft.dropdown.Option("04", "Abril"),
            ft.dropdown.Option("05", "Mayo"),
            ft.dropdown.Option("06", "Junio"),
            ft.dropdown.Option("07", "Julio"),
            ft.dropdown.Option("08", "Agosto"),
            ft.dropdown.Option("09", "Septiembre"),
            ft.dropdown.Option("10", "Octubre"),
            ft.dropdown.Option("11", "Noviembre"),
            ft.dropdown.Option("12", "Diciembre"),
        ],
        value="Todos",
        on_select=lambda e: aplicar_filtros()
    )

    # --- CARGA DE PIEZAS ---
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

    # --- EVENTO DE SELECCIÓN NATIVO ---
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
        
        if registrar_falla_db(dd_sigla_nuevo.value, in_tecnico.value, in_falla.value, in_desc.value, fecha_seleccionada_str):
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
        
        # Cargar las opciones del filtro de aeronaves dinámicamente
        filtro_aeronave.options = [ft.dropdown.Option("Todas")] + [ft.dropdown.Option(a["sigla"]) for a in aviones]
        filtro_aeronave.value = "Todas"

    def actualizar_tabla():
        nonlocal fallas_locales
        fallas_locales = obtener_fallas_db()
        
        # Ordenar de forma segura por fecha (más reciente primero)
        try:
            fallas_locales.sort(key=lambda x: x.get("fecha", ""), reverse=True)
        except:
            pass

        aplicar_filtros()

    def cambiar_pagina(direccion):
        nonlocal pagina_actual
        pagina_actual += direccion
        aplicar_filtros()

    def aplicar_filtros():
        nonlocal pagina_actual
        fallas_filtradas = fallas_locales

        # 1. Filtro por aeronave compatible con ambas llaves de la base de datos
        if filtro_aeronave.value and filtro_aeronave.value != "Todas":
            valor_filtro = str(filtro_aeronave.value).strip().upper()
            
            fallas_filtradas = [
                f for f in fallas_filtradas 
                if (f.get("sigla") and str(f.get("sigla")).strip().upper() == valor_filtro) or 
                   (f.get("aeronave") and str(f.get("aeronave")).strip().upper() == valor_filtro)
            ]

        # 2. Filtro por estado
        if filtro_estado.value and filtro_estado.value != "Todos":
            fallas_filtradas = [f for f in fallas_filtradas if f.get("status") == filtro_estado.value]

        # 3. Filtro por mes (solo evalúa si el registro posee una fecha válida)
        if filtro_mes.value and filtro_mes.value != "Todos":
            fallas_filtradas = [
                f for f in fallas_filtradas 
                if f.get("fecha") and f.get("fecha").split("-")[1] == filtro_mes.value
            ]

        total_registros = len(fallas_filtradas)
        
        # Calcular segmentos para la paginación (Máximo 10 por vista)
        inicio = pagina_actual * REGISTROS_POR_PAGINA
        fin = inicio + REGISTROS_POR_PAGINA
        sublista_paginada = fallas_filtradas[inicio:fin]

        # Actualizar estado de los botones de navegación
        btn_anterior.disabled = pagina_actual == 0
        btn_siguiente.disabled = fin >= total_registros
        
        # Texto de estado: "Mostrando 1-10 de 60"
        if total_registros > 0:
            txt_info_pagina.value = f"Mostrando {inicio + 1} - {min(fin, total_registros)} de {total_registros}"
            txt_info_pagina.visible = True
        else:
            txt_info_pagina.visible = False

        if total_registros == 0:
            tabla_fallas.visible = False
            txt_sin_coincidencias.visible = True
            txt_sin_coincidencias.value = "No se encontraron reportes para los filtros seleccionados."
            btn_anterior.disabled = True
            btn_siguiente.disabled = True
        else:
            tabla_fallas.visible = True
            txt_sin_coincidencias.visible = False
            
            filas_construidas = []
            for indice, f in enumerate(sublista_paginada):
                # Si el índice es par usa el gris oscuro base, si es impar usa una tonalidad un poco más clara
                color_fondo_fila = "#1e293b" if indice % 2 == 0 else "#243249"
                
                # CORRECCIÓN DE FECHA: Si f.get("fecha") no existe o viene vacío, muestra "N/A"
                fecha_registro = f.get("fecha")[:10] if f.get("fecha") else "N/A"
                
                filas_construidas.append(
                    ft.DataRow(
                        color=color_fondo_fila,
                        cells=[
                            ft.DataCell(ft.Text(fecha_registro, color=ft.Colors.BLUE_GREY_100)), 
                            ft.DataCell(ft.Text(f.get("sigla") or f.get("aeronave", ""), weight="bold")),
                            ft.DataCell(ft.Text(f.get("falla", ""))),
                            ft.DataCell(ft.Text(f.get("reportante", ""))),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(f.get("status", ""), size=11, weight="bold", color=ft.Colors.BLACK),
                                    bgcolor=ft.Colors.CYAN_ACCENT if f.get("status") == "Solucionado" else ft.Colors.AMBER_ACCENT,
                                    padding=ft.Padding.symmetric(horizontal=12, vertical=5), 
                                    border_radius=8
                                )
                            ),
                        ]
                    )
                )
            tabla_fallas.rows = filas_construidas
            
        try:
            page.update()
        except:
            pass

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

    # --- FORMULARIO 1: NUEVO REPORTE ---
    form_nuevo = ft.Column([
        ft.Text("Nuevo Reporte de Falla", size=18, weight="bold", color=ft.Colors.CYAN_ACCENT),
        ft.Row([dd_sigla_nuevo, in_tecnico], spacing=20),
        ft.Row([in_falla], spacing=20),
        
        # Nueva fila que junta el campo de texto de la fecha y el botón para abrir el calendario
        ft.Row([
            txt_fecha_visible,
            ft.IconButton(
                icon=ft.Icons.CALENDAR_TODAY, 
                icon_color=ft.Colors.CYAN_ACCENT,
                tooltip="Seleccionar Fecha",
                on_click=lambda _: setattr(picker_calendario, "open", True) or page.update()
            )
        ], spacing=10),
        
        ft.Row([in_desc], spacing=20),
        ft.Row([
            ft.Button("Gestionar Soluciones", icon=ft.Icons.SETTINGS, on_click=lambda _: cambiar_vista(True)),
            ft.Button("Enviar Reporte", icon=ft.Icons.SEND, bgcolor=ft.Colors.CYAN_ACCENT, color=ft.Colors.BLACK, on_click=enviar_reporte_click),
        ], alignment=ft.MainAxisAlignment.END, spacing=15)
    ], spacing=15)

    # --- FORMULARIO 2: REPORTAR SOLUCIÓN ---
    form_solucion = ft.Column([
        ft.Text("Reportar Solución", size=18, weight="bold", color=ft.Colors.GREEN_400),
        ft.Row([dd_reportes_abiertos], spacing=20),
        ft.Row([in_inspector, in_titulo_falla_info], spacing=20),
        ft.Row([dd_estado, dd_piezas_avion], spacing=20),
        ft.Row([in_razon_falla], spacing=20),
        ft.Row([
            ft.TextButton("Registrar Nuevo Reporte", on_click=lambda _: cambiar_vista(False)),
            ft.Button("Guardar Solución", icon=ft.Icons.CHECK, bgcolor=ft.Colors.GREEN_400, color=ft.Colors.BLACK, on_click=guardar_solucion_click),
        ], alignment=ft.MainAxisAlignment.END, spacing=15)
    ], spacing=15, visible=False)

    # Componente de aviso oculto por defecto
    txt_sin_coincidencias = ft.Text(
        "", 
        color=ft.Colors.BLUE_GREY_300, 
        size=14, 
        italic=True, 
        visible=False,
        margin=ft.Margin.only(top=10, bottom=10)
    )

    # --- HISTORIAL ---
    tabla_fallas = ft.DataTable(
        heading_row_height=45,
        data_row_min_height=48,
        horizontal_lines=ft.BorderSide(0, ft.Colors.TRANSPARENT),
        vertical_lines=ft.BorderSide(0, ft.Colors.TRANSPARENT),
        divider_thickness=0,
        columns=[
            ft.DataColumn(ft.Text("Fecha", weight="bold", color=ft.Colors.CYAN_ACCENT)), 
            ft.DataColumn(ft.Text("Aeronave", weight="bold", color=ft.Colors.CYAN_ACCENT)), 
            ft.DataColumn(ft.Text("Falla", weight="bold", color=ft.Colors.CYAN_ACCENT)), 
            ft.DataColumn(ft.Text("Reportante", weight="bold", color=ft.Colors.CYAN_ACCENT)), 
            ft.DataColumn(ft.Text("Estado", weight="bold", color=ft.Colors.CYAN_ACCENT))
        ], 
        rows=[]
    )

    cargar_aviones()
    actualizar_tabla()

    contenedor = ft.Container(
        content=ft.Column([
            create_section_title("Gestión de Reportes", "Control de incidencias y soluciones técnicas"),
            ft.Card(content=ft.Container(padding=30, bgcolor="#1e293b", content=ft.Column([form_nuevo, form_solucion]))),
            
            # --- SECCIÓN DEL HISTORIAL TOTALMENTE CENTRADA ---
            ft.Column([
                # Fila para centrar el título
                ft.Row(
                    [ft.Text("Historial de Incidencias", size=20, weight="bold")],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                
                # Fila para centrar el grupo de filtros
                ft.Row([
                    ft.Text("Filtrar por:", size=14, color=ft.Colors.BLUE_GREY_300, weight="bold"),
                    filtro_aeronave,
                    filtro_estado,
                    filtro_mes
                ], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
                
                # Fila que obliga a la tarjeta contenedora de la tabla a quedarse en el centro de la pantalla
                ft.Row([
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            bgcolor="#1e293b",
                            border_radius=12,
                            content=ft.Column([
                                txt_sin_coincidencias,
                                tabla_fallas,
                                ft.Divider(height=1, color=ft.Colors.BLUE_GREY_800),
                                ft.Row([
                                    txt_info_pagina,
                                    ft.Row([btn_anterior, btn_siguiente], spacing=5)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                        )
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
                
            ], spacing=15, margin=ft.Margin.only(top=20))
            
        ], scroll=ft.ScrollMode.ADAPTIVE),
        padding=40, expand=True, visible=False
    )

    def refresh_data():
        cargar_aviones()
        filtro_aeronave.update()
        dd_sigla_nuevo.update()
        page.update()

    contenedor.refresh_data = refresh_data
    return contenedor