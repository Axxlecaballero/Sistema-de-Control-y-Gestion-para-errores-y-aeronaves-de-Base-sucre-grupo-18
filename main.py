import flet as ft # Importamos flet para la interfaz

def main(page: ft.Page):
    # --- CONFIGURACIÓN DE LA PÁGINA ---
    page.title = "Sistema para fallas y gestión de mantenimiento aeronáutico"
    page.bgcolor = ft.Colors.GREY_700 
    page.theme_mode = ft.ThemeMode.DARK 
    page.padding = 0 
    
    #ÁREA DE CONTENIDO
    # Este contenedor es el que cambiará su contenido según la pestaña seleccionada
    content_area = ft.Container(
        padding=30,
        expand=True,
    )
    # Funciones auxiliares para evitar desplazamiento al registrar
    def registrar_falla(e):
        page.snack_bar = ft.SnackBar(ft.Text("Falla registrada"), open=True)
        page.update()
        page.scroll_to(offset=0)

    def registrar_solucion(e):
        page.snack_bar = ft.SnackBar(ft.Text("Solución registrada"), open=True)
        page.update()
        page.scroll_to(offset=0)
    # --- LÓGICA DE NAVEGACIÓN ---
    # la función se ejecuta cada vez que haces clic en el menú lateral
    def cambiar_pestana(e):
        # Obtenemos el índice del botón presionado
        indice = sidebar.selected_index
        
        # Cambiamos el contenido del área derecha dependiendo del índice
        if indice == 0: # Pestaña Inicio
            content_area.content = ft.Column([
                ft.Text("PANEL DE INICIO", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_100),
                ft.Divider(height=20),
                ft.Text("Bienvenido al sistema de control aeronáutico. Use el menú lateral para gestionar la flota y reportar fallas.", size=16),
            ])
        elif indice == 1: # Pestaña Aeronaves
            content_area.content = ft.Column([
                ft.Text("GESTIÓN DE AERONAVES", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_100),
                ft.Divider(height=20),
                ft.Text("Aquí podrá ver el listado de aviones y su estado de mantenimiento.", size=16),
                ft.Container(height=20),
                ft.Text("Agregar Nueva Aeronave", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_50),
                ft.Row([
                    ft.TextField(label="Sigla de Aeronave", hint_text="Ej. YV-0000", expand=True, border=ft.InputBorder.OUTLINE, border_color=ft.Colors.BLUE_200, focused_border_color=ft.Colors.BLUE_500, fill_color=ft.Colors.GREY_800, color=ft.Colors.WHITE),
                    ft.TextField(label="Horas de Vuelo", value="100", width=150, border=ft.InputBorder.OUTLINE, border_color=ft.Colors.BLUE_200, focused_border_color=ft.Colors.BLUE_500, fill_color=ft.Colors.GREY_800, color=ft.Colors.WHITE),
                    ft.ElevatedButton("Agregar", icon=ft.Icons.ADD, height=50)
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ])
        elif indice == 2: # Pestaña Fallas
            content_area.content = ft.Column([
                ft.Text("CONTROL DE FALLAS Y MANTENIMIENTO", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_100),
                ft.Divider(height=20),
                
                # --- BLOQUE 1: REPORTE DE DETECCIÓN ---
                ft.Text("1. Registro de Detección de Falla", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_300),
                ft.Row([
                    ft.TextField(label="Fecha", hint_text="DD/MM/AAAA", width=150, border=ft.InputBorder.OUTLINE, border_color=ft.Colors.BLUE_200, focused_border_color=ft.Colors.BLUE_500, fill_color=ft.Colors.GREY_800, color=ft.Colors.WHITE),
                    ft.TextField(label="Nombre y Apellido (Inspector)", expand=True, border=ft.InputBorder.OUTLINE, border_color=ft.Colors.BLUE_200, focused_border_color=ft.Colors.BLUE_500, fill_color=ft.Colors.GREY_800, color=ft.Colors.WHITE),
                    ft.TextField(label="Sigla del Avión", hint_text="Ej. YV-123", width=150, border=ft.InputBorder.OUTLINE, border_color=ft.Colors.BLUE_200, focused_border_color=ft.Colors.BLUE_500, fill_color=ft.Colors.GREY_800, color=ft.Colors.WHITE),
                ]),
                ft.TextField(label="Descripción de la Falla Detectada", multiline=True, min_lines=2, border=ft.InputBorder.OUTLINE, border_color=ft.Colors.BLUE_200, focused_border_color=ft.Colors.BLUE_500, fill_color=ft.Colors.GREY_800, color=ft.Colors.WHITE),
                ft.ElevatedButton("Registrar Falla", icon=ft.Icons.REPORT_PROBLEM, bgcolor=ft.Colors.ORANGE_900, color=ft.Colors.WHITE, on_click=registrar_falla),
                
                ft.Divider(height=40, color=ft.Colors.GREY_700), # Separador entre formularios

                # --- BLOQUE 2: REPORTE DE SOLUCIÓN ---
                ft.Text("2. Reporte de Solución de Falla", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_300),
                ft.Row([
                    ft.TextField(label="Fecha", hint_text="DD/MM/AAAA", width=150, border=ft.InputBorder.OUTLINE, border_color=ft.Colors.BLUE_200, focused_border_color=ft.Colors.BLUE_500, fill_color=ft.Colors.GREY_800, color=ft.Colors.WHITE),
                    ft.TextField(label="Nombre y Apellido (Mecánico)", expand=True, border=ft.InputBorder.OUTLINE, border_color=ft.Colors.BLUE_200, focused_border_color=ft.Colors.BLUE_500, fill_color=ft.Colors.GREY_800, color=ft.Colors.WHITE),
                    ft.TextField(label="Sigla del Avión", hint_text="Ej. YV-123", width=150, border=ft.InputBorder.OUTLINE, border_color=ft.Colors.BLUE_200, focused_border_color=ft.Colors.BLUE_500, fill_color=ft.Colors.GREY_800, color=ft.Colors.WHITE),
                ]),
                ft.TextField(label="Descripción de la Solución Técnica", multiline=True, min_lines=2, border=ft.InputBorder.OUTLINE, border_color=ft.Colors.BLUE_200, focused_border_color=ft.Colors.BLUE_500, fill_color=ft.Colors.GREY_800, color=ft.Colors.WHITE),
                ft.ElevatedButton("Registrar Solución", icon=ft.Icons.CHECK_CIRCLE, bgcolor=ft.Colors.GREEN_900, color=ft.Colors.WHITE, on_click=registrar_solucion)
            ], scroll=ft.ScrollMode.AUTO) # Scroll por si la pantalla es pequeña
        page.update() # Actualiza la pantalla para mostrar el cambio

    # --- BARRA LATERAL (NavigationRail) ---
    sidebar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.HOME, label="Inicio"),
            ft.NavigationRailDestination(icon=ft.Icons.FLIGHT_OUTLINED, selected_icon=ft.Icons.HOME, label="Aeronaves"),
            ft.NavigationRailDestination(icon=ft.Icons.BUILD_OUTLINED, selected_icon=ft.Icons.BUILD, label="Fallas"),
        ],
        bgcolor=ft.Colors.GREY_800,
        on_change=cambiar_pestana, # Llamamos a la función al cambiar la selección
    )

    # Cargamos el contenido inicial (Inicio) al arrancar
    cambiar_pestana(None)

    # --- ESTRUCTURA FINAL ---
    page.add(
        ft.Row(
            [
                sidebar,
                ft.VerticalDivider(width=1, color=ft.Colors.GREY_700),
                content_area,
            ],
            expand=True,
        )
    )

# Lanzamos la aplicación
if __name__ == "__main__":
    ft.run(main)