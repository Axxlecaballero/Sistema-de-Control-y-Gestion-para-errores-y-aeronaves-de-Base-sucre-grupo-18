import flet as ft

def create_section_title(title, subtitle):
    return ft.Column([
        ft.Text(title, size=32, weight="bold", color=ft.Colors.WHITE),
        ft.Text(subtitle, size=16, color=ft.Colors.BLUE_GREY_200),
        ft.Divider(height=30, color=ft.Colors.WHITE_12)
    ], spacing=5)

def aircraft_card(sigla, horas, max_horas, prox_inspeccion, on_sumar_click, on_insp_click, on_delete_click, on_piezas_click=None):
    # --- LÓGICA DINÁMICA DE PRÓRROGA Y ESTADOS ---
    limite_base = prox_inspeccion
    prorroga = 10
    limite_total = limite_base + prorroga
    
    # Calculamos las diferencias
    faltan_insp = limite_base - horas
    faltan_vida = max_horas - horas
    horas_ciclo = round(100.0 - faltan_insp, 2)
    if horas_ciclo < 0: horas_ciclo = 0
    
    vida_alcanzada = horas >= max_horas
    
    if vida_alcanzada:
        estado = "VIDA ÚTIL ALCANZADA"
        color_tema = ft.Colors.DEEP_PURPLE_400
        porcentaje = 1.0
    elif horas >= limite_total:
        estado = "VENCIDO"
        color_tema = ft.Colors.RED_ACCENT
        porcentaje = 1.0
    elif horas >= limite_base:
        estado = "EN PRÓRROGA"
        color_tema = ft.Colors.RED_400
        porcentaje = 1.0
    elif faltan_insp <= 10: # Si faltan 10 horas o menos
        estado = "INSP. PRÓXIMA"
        color_tema = ft.Colors.ORANGE_400
        porcentaje = horas_ciclo / 100.0
    else:
        estado = "OPERATIVO"
        color_tema = ft.Colors.CYAN_ACCENT
        porcentaje = horas_ciclo / 100.0

    if porcentaje < 0: porcentaje = 0
    if porcentaje > 1: porcentaje = 1

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.AIRPLANEMODE_ACTIVE, color=color_tema, size=30),
                ft.Text(sigla, size=20, weight="bold"),
                ft.Container(
                    content=ft.Text(
                        estado, 
                        size=10, weight="bold", 
                        color=ft.Colors.WHITE if estado in ["VENCIDO", "VIDA ÚTIL ALCANZADA"] else ft.Colors.BLACK
                    ),
                    bgcolor=color_tema,
                    padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                    border_radius=5
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Text(
                f"Desde última Insp: {horas_ciclo} / 100 hr " + (f"(En prórroga)" if horas >= limite_base else ""), 
                size=14, color=ft.Colors.BLUE_GREY_100
            ),
            ft.Text(
                f"Vida Restante: {faltan_vida} hr (Total: {max_horas})", 
                size=12, color=ft.Colors.AMBER_400
            ),
            ft.ProgressBar(value=porcentaje, color=color_tema, bgcolor=ft.Colors.WHITE_10, height=8),
            
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.RED_400,
                    tooltip="Eliminar Aeronave",
                    on_click=lambda _: on_delete_click(sigla)
                ),
                ft.Row([
                    ft.TextButton(
                        "Piezas",
                        icon=ft.Icons.SETTINGS,
                        style=ft.ButtonStyle(color=ft.Colors.AMBER_400),
                        on_click=lambda _: on_piezas_click(sigla) if on_piezas_click else None,
                        disabled=vida_alcanzada
                    ),
                    ft.TextButton(
                        "Insp.", 
                        icon=ft.Icons.BUILD_CIRCLE,
                        style=ft.ButtonStyle(color=ft.Colors.BLUE_GREY_200),
                        on_click=lambda _: on_insp_click(sigla),
                        disabled=vida_alcanzada
                    ),
                    ft.TextButton(
                        "+ Horas", 
                        icon=ft.Icons.ADD, 
                        style=ft.ButtonStyle(color=color_tema),
                        on_click=lambda _: on_sumar_click(sigla),
                        disabled=vida_alcanzada
                    )
                ], spacing=0, wrap=True)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], spacing=15),
        padding=20,
        bgcolor="#1e293b",
        border_radius=15,
        border=ft.Border.all(1, ft.Colors.WHITE_10),
    )

def pieza_card(pieza, on_sumar_click):
    horas = pieza["horas_pieza"]
    if horas < 90:
        estado = "OPERATIVO"
        color_tema = ft.Colors.CYAN_ACCENT
    elif horas < 100:
        estado = "CRÍTICO"
        color_tema = ft.Colors.ORANGE_400
    elif horas < 110:
        estado = "EN PRÓRROGA"
        color_tema = ft.Colors.RED_400
    else:
        estado = "VENCIDO"
        color_tema = ft.Colors.RED_ACCENT

    porcentaje = min(horas / 110.0, 1.0)
    
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SETTINGS, color=color_tema, size=24),
                ft.Text(pieza["nombre_pieza"], size=16, weight="bold", expand=1),
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
            
            ft.Text(f"P/N: {pieza['numero_parte']} | S/N: {pieza['numero_serie']}", size=12, color=ft.Colors.BLUE_GREY_200),
            ft.Text(f"Fabricante: {pieza['fabricante']}", size=12, color=ft.Colors.BLUE_GREY_200),
            ft.Text(
                f"Horas de Vuelo: {horas} / 100 hr " + (f"(En prórroga)" if 100 <= horas < 110 else ""), 
                size=14, color=ft.Colors.BLUE_GREY_100
            ),
            ft.Text(
                f"Vida Restante: {round(100.0 - horas, 2)} hr (Total: 100.0)", 
                size=12, color=ft.Colors.AMBER_400
            ),
            ft.ProgressBar(value=porcentaje, color=color_tema, bgcolor=ft.Colors.WHITE_10, height=6),
            
            ft.Row([
                ft.Button(
                    "Sumar Horas", 
                    icon=ft.Icons.ADD, 
                    style=ft.ButtonStyle(color=color_tema),
                    on_click=lambda _: on_sumar_click(pieza["id_pieza"], pieza["nombre_pieza"])
                )
            ], alignment=ft.MainAxisAlignment.END)
        ], spacing=10),
        padding=15,
        bgcolor="#1e293b",
        border_radius=10,
        border=ft.Border.all(1, ft.Colors.WHITE_10),
    )

