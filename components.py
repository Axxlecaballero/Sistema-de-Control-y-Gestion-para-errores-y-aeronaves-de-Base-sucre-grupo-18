import flet as ft

def create_section_title(title, subtitle):
    return ft.Column([
        ft.Text(title, size=32, weight="bold", color=ft.Colors.WHITE),
        ft.Text(subtitle, size=16, color=ft.Colors.BLUE_GREY_200),
        ft.Divider(height=30, color=ft.Colors.WHITE_12)
    ], spacing=5)

def aircraft_card(sigla, horas, max_horas, prox_inspeccion, on_sumar_click, on_insp_click):
    # --- LÓGICA DINÁMICA DE PRÓRROGA Y ESTADOS ---
    limite_base = prox_inspeccion
    prorroga = 10
    limite_total = limite_base + prorroga
    
    # Calculamos la diferencia para saber cuánto falta para la inspección
    faltan = limite_base - horas
    
    if horas >= limite_total:
        estado = "VENCIDO"
        color_tema = ft.Colors.RED_ACCENT
        porcentaje = 1.0
    elif horas >= limite_base:
        estado = "EN PRÓRROGA"
        color_tema = ft.Colors.RED_400
        porcentaje = (horas - (limite_base - max_horas)) / (max_horas + prorroga)
    elif faltan <= 10: # Si faltan 10 horas o menos
        estado = "CRÍTICO"
        color_tema = ft.Colors.ORANGE_400
        porcentaje = (horas - (limite_base - max_horas)) / max_horas
    else:
        estado = "OPERATIVO"
        color_tema = ft.Colors.CYAN_ACCENT
        porcentaje = (horas - (limite_base - max_horas)) / max_horas

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
                ft.TextButton(
                    "Inspección", 
                    icon=ft.Icons.BUILD_CIRCLE,
                    style=ft.ButtonStyle(color=ft.Colors.BLUE_GREY_200),
                    on_click=lambda _: on_insp_click(sigla)
                ),
                ft.Button(
                    "Sumar Horas", 
                    icon=ft.Icons.ADD, 
                    style=ft.ButtonStyle(color=color_tema),
                    on_click=lambda _: on_sumar_click(sigla)
                ),
            ], alignment=ft.MainAxisAlignment.END, spacing=0)
        ], spacing=15),
        padding=20,
        bgcolor="#1e293b",
        border_radius=15,
        border=ft.Border.all(1, ft.Colors.WHITE_10),
    )
