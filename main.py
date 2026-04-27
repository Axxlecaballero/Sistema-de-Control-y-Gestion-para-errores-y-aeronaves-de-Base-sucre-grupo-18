import flet as ft # Importamos flet para la interfaz

def main(page: ft.Page):
    # --- CONFIGURACIÓN DE LA PÁGINA ---
    page.title = "Sistema para fallas y gestión de mantenimiento aeronáutico"
    page.bgcolor = ft.Colors.GREY_900 
    page.theme_mode = ft.ThemeMode.DARK 
    page.padding = 0 
    
    #ÁREA DE CONTENIDO
    # Este contenedor es el que cambiará su contenido según la pestaña seleccionada
    content_area = ft.Container(
        padding=30,
        expand=True,
    )

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
            ])
        elif indice == 2: # Pestaña Fallas
            content_area.content = ft.Column([
                ft.Text("CONTROL DE FALLAS", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_100),
                ft.Divider(height=20),
                ft.Text("Registro de incidencias técnicas y fallas detectadas por aeronave.", size=16),
            ])
        page.update() # Actualiza la pantalla para mostrar el cambio

    # --- BARRA LATERAL (NavigationRail) ---
    sidebar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.HOME, label="Inicio"),
            ft.NavigationRailDestination(icon=ft.Icons.FLIGHT_OUTLINED, selected_icon=ft.Icons.FLIGHT, label="Aeronaves"),
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
    ft.app(target=main)
