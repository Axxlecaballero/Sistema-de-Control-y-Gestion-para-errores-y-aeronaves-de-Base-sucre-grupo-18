import flet as ft

def main(page: ft.Page):
    # Configuración básica de la ventana
    page.title = "Sistema de Gestión Aeronáutica"
    page.theme_mode = ft.ThemeMode.DARK 
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # Un texto de bienvenida
    bienvenida = ft.Text(
        "Sistema Control de Fallas de aerona v1.0",
        size=30,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_200 
    )

    Subtitulo = ft.Text(
        "¡Bienvenido al sistema de gestión aeronáutica! Aquí podrás registrar y gestionar las fallas de las aeronaves de manera eficiente.",
        size=16,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.RED_300
    )
    # Un botón de prueba
    boton_prueba = ft.ElevatedButton(
        "Comenzar Registro",
        color =ft.Colors.GREEN_400,
        icon=ft.Icons.AIRPLANEMODE_ACTIVE,
        on_click=lambda _: print("¡Botón presionado!")
    )

    # Añadir elementos a la página con diseño centrado
    page.add(
        ft.Column(
            [
                bienvenida,
                ft.Divider(height=20, color="transparent"), # Espacio invisible
                boton_prueba,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    page.add(
        ft.Column(
            [
                Subtitulo,
                ft.Divider(height=20, color="transparent"), # Espacio invisible
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

# Ejecutar la aplicación
ft.app(target=main)