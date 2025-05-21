import flet as ft
from weather_service import WeatherService

def main(page: ft.Page):
    # Configure the page
    page.title = "Weather Tracker Dashboard"
    page.theme_mode = "light"
    page.padding = 20
    page.window_width = 400
    page.window_height = 800
    page.window_resizable = True
    page.scroll = True

    # Initialize weather service
    weather_service = WeatherService()

    # Create UI components
    city_input = ft.TextField(
        label="Enter city name",
        hint_text="e.g., London",
        width=300,
        border_radius=10,
        text_size=16
    )

    weather_card = ft.Container(
        visible=False,
        bgcolor=ft.colors.WHITE,
        border_radius=10,
        padding=20,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.colors.BLUE_GREY_100,
        )
    )

    error_text = ft.Text(
        color="red",
        size=14,
        visible=False
    )

    def create_weather_content(weather_data):
        if "error" in weather_data:
            error_text.value = weather_data["error"]
            error_text.visible = True
            weather_card.visible = False
            page.update()
            return

        error_text.visible = False
        weather_card.visible = True
        
        # Create weather icon URL
        icon_code = weather_data["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

        weather_card.content = ft.Column(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            f"{weather_data['city']}, {weather_data['country']}",
                            size=24,
                            weight=ft.FontWeight.BOLD
                        )
                    ]
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Image(
                            src=icon_url,
                            width=100,
                            height=100,
                        )
                    ]
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            f"{weather_data['temperature']}°C",
                            size=48,
                            weight=ft.FontWeight.BOLD
                        )
                    ]
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            weather_data['description'].capitalize(),
                            size=20,
                        )
                    ]
                ),
                ft.Divider(height=20, color=ft.colors.BLUE_GREY_100),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Feels Like", size=16),
                                ft.Text(f"{weather_data['feels_like']}°C", size=20, weight=ft.FontWeight.BOLD)
                            ]
                        ),
                        ft.Column(
                            controls=[
                                ft.Text("Humidity", size=16),
                                ft.Text(f"{weather_data['humidity']}%", size=20, weight=ft.FontWeight.BOLD)
                            ]
                        ),
                        ft.Column(
                            controls=[
                                ft.Text("Wind Speed", size=16),
                                ft.Text(f"{weather_data['wind_speed']} m/s", size=20, weight=ft.FontWeight.BOLD)
                            ]
                        )
                    ]
                )
            ]
        )
        page.update()

    def search_weather(e):
        if not city_input.value:
            error_text.value = "Please enter a city name"
            error_text.visible = True
            weather_card.visible = False
            page.update()
            return

        weather_data = weather_service.get_weather(city_input.value)
        create_weather_content(weather_data)

    search_btn = ft.ElevatedButton(
        "Search",
        on_click=search_weather,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE,
            padding=15,
        )
    )

    # Add components to page
    page.add(
        ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Weather Tracker", size=32, weight=ft.FontWeight.BOLD),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[city_input, search_btn]
                ),
                error_text,
                weather_card
            ]
        )
    )

ft.app(target=main, view=ft.WEB_BROWSER) 