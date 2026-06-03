import flet as ft
from components import create_section_title
from database import (
    obtener_estadisticas_fallas, 
    obtener_fallas_por_aeronave_detalle, 
    obtener_aeronaves, 
    obtener_fallas_por_pieza_en_periodo
)

def get_estadisticas_view(page: ft.Page):
    
    # --- ESTADO INTERNO ---
    detalle_sigla_actual = None

    # --- COLORES POR POSICION EN RANKING ---
    COLORES_BARRAS = [
        "#ef4444",   # Rojo - 1ro (mas fallas)
        "#f97316",   # Naranja - 2do
        "#eab308",   # Amarillo - 3ro
        "#06b6d4",   # Cyan - 4to
        "#3b82f6",   # Azul - 5to+
    ]

    def color_para_posicion(idx):
        if idx < len(COLORES_BARRAS):
            return COLORES_BARRAS[idx]
        return "#3b82f6"

    # --- GRAFICO DE BARRAS PERSONALIZADO ---
    CHART_MAX_HEIGHT = 250
    grafico_barras_row = ft.Row(
        [], spacing=12,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.END,
    )

    txt_sin_datos_grafico = ft.Text(
        "No hay fallas registradas.",
        color=ft.Colors.BLUE_GREY_400, size=14, italic=True,
        text_align=ft.TextAlign.CENTER, visible=False
    )

    grafico_card = ft.Container(
        padding=25,
        bgcolor="#1e293b",
        border_radius=12,
        border=ft.Border.all(1, ft.Colors.WHITE_10),
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.BAR_CHART, color=ft.Colors.CYAN_ACCENT, size=22),
                ft.Text("Fallas por Aeronave", size=16, weight="bold", color=ft.Colors.CYAN_ACCENT),
            ], spacing=10),
            grafico_barras_row,
            txt_sin_datos_grafico,
        ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    # --- RESUMEN RAPIDO (KPIs) ---
    kpi_total_fallas = ft.Text("0", size=28, weight="bold", color=ft.Colors.CYAN_ACCENT)
    kpi_pendientes = ft.Text("0", size=28, weight="bold", color=ft.Colors.AMBER_ACCENT)
    kpi_solucionadas = ft.Text("0", size=28, weight="bold", color=ft.Colors.GREEN_400)
    kpi_aeronaves = ft.Text("0", size=28, weight="bold", color=ft.Colors.BLUE_ACCENT)

    def crear_kpi_card(titulo, valor_widget, icono, color_icono):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icono, color=color_icono, size=20),
                    ft.Text(titulo, size=12, color=ft.Colors.BLUE_GREY_300, weight="bold"),
                ], spacing=8),
                valor_widget,
            ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor="#1e293b",
            border_radius=12,
            border=ft.Border.all(1, ft.Colors.WHITE_10),
            expand=True,
        )

    kpis_row = ft.Row([
        crear_kpi_card("Total Fallas", kpi_total_fallas, ft.Icons.WARNING_AMBER, ft.Colors.CYAN_ACCENT),
        crear_kpi_card("Pendientes", kpi_pendientes, ft.Icons.PENDING_ACTIONS, ft.Colors.AMBER_ACCENT),
        crear_kpi_card("Solucionadas", kpi_solucionadas, ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN_400),
        crear_kpi_card("Aeronaves Afectadas", kpi_aeronaves, ft.Icons.FLIGHT, ft.Colors.BLUE_ACCENT),
    ], spacing=15)

    # --- RANKING / LISTA DE AERONAVES ---
    ranking_column = ft.Column([], spacing=10)

    txt_sin_datos_ranking = ft.Text(
        "No hay aeronaves con fallas registradas.",
        color=ft.Colors.BLUE_GREY_400, size=14, italic=True,
        text_align=ft.TextAlign.CENTER, visible=False
    )

    ranking_card = ft.Container(
        padding=25,
        bgcolor="#1e293b",
        border_radius=12,
        border=ft.Border.all(1, ft.Colors.WHITE_10),
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.LEADERBOARD, color=ft.Colors.CYAN_ACCENT, size=22),
                ft.Text("Ranking de Aeronaves con Mas Fallas", size=16, weight="bold", color=ft.Colors.CYAN_ACCENT),
                ft.Text("Presione una aeronave para ver el detalle", size=12, color=ft.Colors.BLUE_GREY_400, italic=True),
            ], spacing=10),
            txt_sin_datos_ranking,
            ranking_column,
        ], spacing=15)
    )

    # --- PANEL DE DETALLE DE FALLAS ---
    detalle_titulo = ft.Text("", size=18, weight="bold", color=ft.Colors.CYAN_ACCENT)
    detalle_tabla = ft.DataTable(
        heading_row_height=45,
        data_row_min_height=48,
        horizontal_lines=ft.BorderSide(0, ft.Colors.TRANSPARENT),
        vertical_lines=ft.BorderSide(0, ft.Colors.TRANSPARENT),
        divider_thickness=0,
        columns=[
            ft.DataColumn(ft.Text("Fecha", weight="bold", color=ft.Colors.CYAN_ACCENT)),
            ft.DataColumn(ft.Text("Titulo", weight="bold", color=ft.Colors.CYAN_ACCENT)),
            ft.DataColumn(ft.Text("Reportante", weight="bold", color=ft.Colors.CYAN_ACCENT)),
            ft.DataColumn(ft.Text("Estado", weight="bold", color=ft.Colors.CYAN_ACCENT)),
        ],
        rows=[]
    )
    txt_sin_detalle = ft.Text(
        "Esta aeronave no tiene fallas registradas.",
        color=ft.Colors.BLUE_GREY_400, size=14, italic=True, visible=False
    )

    detalle_card = ft.Container(
        padding=25,
        bgcolor="#162032",
        border_radius=12,
        border=ft.Border.all(1, ft.Colors.CYAN_ACCENT),
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.LIST_ALT, color=ft.Colors.CYAN_ACCENT, size=22),
                detalle_titulo,
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=ft.Colors.BLUE_GREY_300,
                    tooltip="Cerrar detalle",
                    on_click=lambda e: cerrar_detalle(e)
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            txt_sin_detalle,
            detalle_tabla,
        ], spacing=15),
        visible=False
    )

    def cerrar_detalle(e):
        nonlocal detalle_sigla_actual
        detalle_sigla_actual = None
        detalle_card.visible = False
        try:
            page.update()
        except:
            pass

    def mostrar_detalle(sigla):
        nonlocal detalle_sigla_actual
        detalle_sigla_actual = sigla
        detalle_titulo.value = f"Fallas de {sigla}"

        fallas = obtener_fallas_por_aeronave_detalle(sigla)

        if not fallas:
            detalle_tabla.visible = False
            txt_sin_detalle.visible = True
        else:
            txt_sin_detalle.visible = False
            detalle_tabla.visible = True
            filas = []
            for idx, f in enumerate(fallas):
                color_fondo = "#1e293b" if idx % 2 == 0 else "#243249"
                fecha_val = f.get("fecha", "")
                fecha_display = fecha_val[:10] if fecha_val else "N/A"
                status = f.get("status", "")

                filas.append(
                    ft.DataRow(
                        color=color_fondo,
                        cells=[
                            ft.DataCell(ft.Text(fecha_display, color=ft.Colors.BLUE_GREY_100)),
                            ft.DataCell(ft.Text(f.get("titulo_falla", ""), weight="bold")),
                            ft.DataCell(ft.Text(f.get("reportante", ""))),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(
                                        status, size=11, weight="bold",
                                        color=ft.Colors.BLACK
                                    ),
                                    bgcolor=ft.Colors.GREEN_400 if status == "Solucionado" else ft.Colors.AMBER_ACCENT,
                                    padding=ft.Padding.symmetric(horizontal=12, vertical=5),
                                    border_radius=8
                                )
                            ),
                        ]
                    )
                )
            detalle_tabla.rows = filas

        detalle_card.visible = True
        try:
            page.update()
        except:
            pass

    # --- FUNCION: CONSTRUIR BARRAS DEL GRAFICO ---
    def construir_grafico(datos):
        grafico_barras_row.controls.clear()

        if not datos:
            grafico_barras_row.visible = False
            txt_sin_datos_grafico.visible = True
            return

        grafico_barras_row.visible = True
        txt_sin_datos_grafico.visible = False

        max_fallas = max(d["total_fallas"] for d in datos)
        if max_fallas == 0:
            max_fallas = 1

        num_barras = len(datos)
        bar_width = max(35, min(65, 600 // max(num_barras, 1)))

        for idx, d in enumerate(datos):
            sigla = d["sigla"]
            total_f = d["total_fallas"]
            pend = d["pendientes"]
            sol = d["solucionadas"]
            color = color_para_posicion(idx)

            bar_height_pend = (pend / max_fallas) * CHART_MAX_HEIGHT if max_fallas > 0 else 0
            bar_height_sol = (sol / max_fallas) * CHART_MAX_HEIGHT if max_fallas > 0 else 0

            stack_items = []
            if pend > 0:
                pct_pend = int((pend / total_f) * 100)
                txt_pend = ft.Text(f"{pct_pend}%", size=9, weight="bold", color=ft.Colors.WHITE) if bar_height_pend > 15 and bar_width > 20 else None
                stack_items.append(
                    ft.Container(
                        content=txt_pend,
                        alignment=ft.Alignment(0, 0),
                        width=bar_width,
                        height=max(bar_height_pend, 6),
                        bgcolor="#f59e0b",
                        border_radius=ft.BorderRadius.only(
                            top_left=6, top_right=6,
                            bottom_left=0 if sol > 0 else 4,
                            bottom_right=0 if sol > 0 else 4,
                        ),
                        tooltip=f"{sigla}: {pend} pendientes ({pct_pend}%)",
                    )
                )
            if sol > 0:
                pct_sol = int((sol / total_f) * 100)
                txt_sol = ft.Text(f"{pct_sol}%", size=9, weight="bold", color=ft.Colors.WHITE) if bar_height_sol > 15 and bar_width > 20 else None
                stack_items.append(
                    ft.Container(
                        content=txt_sol,
                        alignment=ft.Alignment(0, 0),
                        width=bar_width,
                        height=max(bar_height_sol, 6),
                        bgcolor="#22c55e",
                        border_radius=ft.BorderRadius.only(
                            top_left=6 if pend == 0 else 0,
                            top_right=6 if pend == 0 else 0,
                            bottom_left=4, bottom_right=4,
                        ),
                        tooltip=f"{sigla}: {sol} solucionadas ({pct_sol}%)",
                    )
                )

            def hacer_click_barra(s=sigla):
                return lambda e: mostrar_detalle(s)

            barra_completa = ft.Container(
                content=ft.Column([
                    ft.Text(
                        str(total_f), size=13, weight="bold", color=color,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Column(
                        stack_items,
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(
                        content=ft.Text(
                            sigla, size=11, weight="bold",
                            color=ft.Colors.BLUE_GREY_200,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        bgcolor="#0f172a",
                        padding=ft.Padding.symmetric(horizontal=6, vertical=3),
                        border_radius=4,
                    ),
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   alignment=ft.MainAxisAlignment.END),
                on_click=hacer_click_barra(),
                ink=True,
                tooltip=f"{sigla}: {total_f} fallas ({pend} pendientes, {sol} solucionadas)",
                padding=ft.Padding.only(bottom=5),
            )
            grafico_barras_row.controls.append(barra_completa)

    # --- FUNCION PRINCIPAL DE ACTUALIZACION ---
    def actualizar_estadisticas():
        datos = obtener_estadisticas_fallas()

        total = sum(d["total_fallas"] for d in datos)
        pendientes = sum(d["pendientes"] for d in datos)
        solucionadas = sum(d["solucionadas"] for d in datos)

        kpi_total_fallas.value = str(total)
        kpi_pendientes.value = str(pendientes)
        kpi_solucionadas.value = str(solucionadas)
        kpi_aeronaves.value = str(len(datos))

        construir_grafico(datos)

        if not datos:
            txt_sin_datos_ranking.visible = True
            ranking_column.controls.clear()
        else:
            txt_sin_datos_ranking.visible = False
            ranking_column.controls.clear()

            for idx, d in enumerate(datos):
                sigla = d["sigla"]
                total_f = d["total_fallas"]
                pend = d["pendientes"]
                sol = d["solucionadas"]
                color = color_para_posicion(idx)
                posicion = idx + 1

                max_f_ranking = datos[0]["total_fallas"] if datos else 1
                barra_progreso_pct = total_f / max_f_ranking if max_f_ranking > 0 else 0

                def hacer_click(s=sigla):
                    return lambda e: mostrar_detalle(s)

                ranking_item = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Text(f"#{posicion}", size=14, weight="bold", color=ft.Colors.WHITE),
                                width=40, height=40,
                                bgcolor=color,
                                border_radius=20,
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Column([
                                ft.Text(sigla, size=16, weight="bold"),
                                ft.Text(
                                    f"{total_f} fallas  |  {pend} pendientes  |  {sol} solucionadas",
                                    size=12, color=ft.Colors.BLUE_GREY_300
                                ),
                            ], spacing=2, expand=True),
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(str(total_f), size=22, weight="bold", color=color),
                                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.BLUE_GREY_400),
                                ], spacing=5),
                            ),
                        ], spacing=15, alignment=ft.MainAxisAlignment.START),
                        ft.ProgressBar(
                            value=barra_progreso_pct,
                            color=color,
                            bgcolor=ft.Colors.WHITE_10,
                            height=4,
                        ),
                    ], spacing=10),
                    padding=ft.Padding.symmetric(horizontal=20, vertical=15),
                    bgcolor="#243249" if idx % 2 == 0 else "#1e293b",
                    border_radius=10,
                    border=ft.Border.all(1, ft.Colors.WHITE_10),
                    on_click=hacer_click(),
                    ink=True,
                )
                ranking_column.controls.append(ranking_item)

        if detalle_sigla_actual:
            mostrar_detalle(detalle_sigla_actual)

        try:
            page.update()
        except:
            pass

    # Leyenda eliminada según solicitud

    # --- NUEVA SECCION: FALLAS POR PIEZA Y PERIODO ---
    dd_aeronave_stats = ft.Dropdown(label="Aeronave", width=200, border_color=ft.Colors.BLUE_GREY_700)
    dd_periodo_stats = ft.Dropdown(
        label="Periodo de Tiempo", 
        width=200, 
        border_color=ft.Colors.BLUE_GREY_700,
        options=[
            ft.dropdown.Option("ultima_semana", "Última Semana"),
            ft.dropdown.Option("ultimo_mes", "Último Mes"),
            ft.dropdown.Option("ultimos_6_meses", "Últimos 6 Meses"),
            ft.dropdown.Option("ultimo_anio", "Último Año"),
            ft.dropdown.Option("ultimos_2_anios", "Últimos 2 Años"),
            ft.dropdown.Option("ultimos_6_anios", "Últimos 6 Años"),
        ],
        value="ultimo_mes"
    )
    
    tabla_piezas_stats = ft.DataTable(
        heading_row_height=45,
        data_row_min_height=48,
        horizontal_lines=ft.BorderSide(0, ft.Colors.TRANSPARENT),
        vertical_lines=ft.BorderSide(0, ft.Colors.TRANSPARENT),
        divider_thickness=0,
        columns=[
            ft.DataColumn(ft.Text("Pieza", weight="bold", color=ft.Colors.CYAN_ACCENT)),
            ft.DataColumn(ft.Text("Nro. Parte", weight="bold", color=ft.Colors.CYAN_ACCENT)),
            ft.DataColumn(ft.Text("Fallas", weight="bold", color=ft.Colors.CYAN_ACCENT)),
        ],
        rows=[]
    )
    
    txt_sin_piezas = ft.Text("No hay datos para el periodo seleccionado.", color=ft.Colors.BLUE_GREY_400, italic=True, visible=False)
    
    grafico_piezas_row = ft.Row(
        [], spacing=12,
        scroll=ft.ScrollMode.ADAPTIVE,
        vertical_alignment=ft.CrossAxisAlignment.END,
    )
    
    def actualizar_stats_piezas(e=None):
        if not dd_aeronave_stats.value:
            return
            
        datos_piezas = obtener_fallas_por_pieza_en_periodo(dd_aeronave_stats.value, dd_periodo_stats.value)
        
        tabla_piezas_stats.rows.clear()
        
        if not datos_piezas:
            tabla_piezas_stats.visible = False
            grafico_piezas_row.visible = False
            txt_sin_piezas.visible = True
        else:
            tabla_piezas_stats.visible = True
            grafico_piezas_row.visible = True
            txt_sin_piezas.visible = False
            
            # Construir grafico
            grafico_piezas_row.controls.clear()
            # Filtrar solo piezas con fallas
            piezas_con_fallas = [p for p in datos_piezas if p["total_fallas"] > 0]
            
            if not piezas_con_fallas:
                grafico_piezas_row.visible = False
                txt_sin_piezas.value = "No se registraron fallas en ninguna pieza en este periodo."
                txt_sin_piezas.visible = True
            else:
                grafico_piezas_row.visible = True
                txt_sin_piezas.visible = False
                max_f_pieza = max(p["total_fallas"] for p in piezas_con_fallas)
                
                for p in piezas_con_fallas:
                    nombre_corto = p["nombre_pieza"][:12] + "..." if len(p["nombre_pieza"]) > 12 else p["nombre_pieza"]
                    alto_barra = (p["total_fallas"] / max_f_pieza) * 150
                    
                    barra = ft.Container(
                        content=ft.Column([
                            ft.Text(str(p["total_fallas"]), size=12, weight="bold", color=ft.Colors.AMBER_400),
                            ft.Container(
                                width=45,
                                height=max(alto_barra, 6),
                                bgcolor=ft.Colors.AMBER_400,
                                border_radius=4,
                                tooltip=f"{p['nombre_pieza']}: {p['total_fallas']} fallas"
                            ),
                            ft.Container(
                                content=ft.Text(nombre_corto, size=10, color=ft.Colors.BLUE_GREY_300, text_align=ft.TextAlign.CENTER),
                                width=45
                            )
                        ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.END)
                    )
                    grafico_piezas_row.controls.append(barra)
            
            # Llenar tabla
            for idx, p in enumerate(datos_piezas):
                color_fondo = "#1e293b" if idx % 2 == 0 else "#243249"
                tabla_piezas_stats.rows.append(
                    ft.DataRow(
                        color=color_fondo,
                        cells=[
                            ft.DataCell(ft.Text(p["nombre_pieza"], weight="bold")),
                            ft.DataCell(ft.Text(p["numero_parte"])),
                            ft.DataCell(ft.Text(str(p["total_fallas"]), color=ft.Colors.AMBER_400 if p["total_fallas"] > 0 else ft.Colors.BLUE_GREY_200, weight="bold")),
                        ]
                    )
                )
        try:
            page.update()
        except:
            pass

    dd_aeronave_stats.on_select = actualizar_stats_piezas
    dd_periodo_stats.on_select = actualizar_stats_piezas

    piezas_stats_card = ft.Container(
        padding=25,
        bgcolor="#1e293b",
        border_radius=12,
        border=ft.Border.all(1, ft.Colors.WHITE_10),
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.BUILD_CIRCLE, color=ft.Colors.CYAN_ACCENT, size=22),
                ft.Text("Fallas por Pieza en Periodo", size=16, weight="bold", color=ft.Colors.CYAN_ACCENT),
            ], spacing=10),
            ft.Row([dd_aeronave_stats, dd_periodo_stats], spacing=20),
            txt_sin_piezas,
            grafico_piezas_row,
            ft.Divider(height=1, color=ft.Colors.WHITE_10),
            tabla_piezas_stats,
        ], spacing=15)
    )

    # --- CONTENEDOR PRINCIPAL ---
    contenedor = ft.Container(
        content=ft.Column([
            create_section_title("Estadisticas", "Analisis de fallas reportadas por aeronave"),
            kpis_row,
            grafico_card,
            ranking_card,
            detalle_card,
            piezas_stats_card,
        ], scroll=ft.ScrollMode.ADAPTIVE, spacing=20),
        padding=40, expand=True, visible=False
    )

    def refresh_data():
        actualizar_estadisticas()
        
        # Cargar aviones en dropdown de nueva seccion
        aviones = obtener_aeronaves()
        dd_aeronave_stats.options = [ft.dropdown.Option(a["sigla"]) for a in aviones]
        if aviones and not dd_aeronave_stats.value:
            dd_aeronave_stats.value = aviones[0]["sigla"]
            actualizar_stats_piezas()
        dd_aeronave_stats.update()


    contenedor.refresh_data = refresh_data

    actualizar_estadisticas()

    return contenedor
