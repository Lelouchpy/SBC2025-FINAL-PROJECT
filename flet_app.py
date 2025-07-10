import flet as ft
import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder

def main(page: ft.Page):
    page.title = "Car Price Predictor"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    try:
        model_data = joblib.load('car_price_model.pkl')
        model = model_data['model']
        encoders = model_data['encoders']
        model_loaded = True
    except Exception as e:
        print(f"Error loading model: {e}")
        model_loaded = False

    dropdown_options = {
        'fuel_types': ['gas', 'diesel'],
        'aspirations': ['std', 'turbo'],
        'doors': ['two', 'four'],
        'bodies': ['convertible', 'sedan', 'hatchback', 'wagon', 'hardtop'],
        'drive_wheels': ['rwd', 'fwd', '4wd'],
        'engine_locations': ['front', 'rear'],
        'engine_types': ['dohc', 'ohcv', 'ohc', 'l', 'rotor', 'ohcf'],
        'cylinders': ['four', 'six', 'five', 'three', 'twelve', 'two', 'eight'],
        'fuel_systems': ['mpfi', '2bbl', 'mfi', '1bbl', 'spfi', '4bbl', 'idi', 'spdi']
    }

    def create_numeric_field(label, min_val, max_val, default):
        return ft.TextField(
            label=f"{label} ({min_val}-{max_val})",
            value=str(default),
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.NumbersOnlyInputFilter(),
            expand=True,
            border_radius=10,
            border_width=1
        )

    symboling = create_numeric_field("Symboling", -2, 3, 0)
    fuel_type = ft.Dropdown(
        label="Fuel Type", 
        options=[ft.dropdown.Option(t.capitalize()) for t in dropdown_options['fuel_types']],
        border_radius=10,
        border_width=1
    )
    aspiration = ft.Dropdown(
        label="Aspiration", 
        options=[ft.dropdown.Option(t.capitalize()) for t in dropdown_options['aspirations']],
        border_radius=10,
        border_width=1
    )
    doors = ft.Dropdown(
        label="Doors", 
        options=[ft.dropdown.Option(t.capitalize()) for t in dropdown_options['doors']],
        border_radius=10,
        border_width=1
    )
    body = ft.Dropdown(
        label="Body Style", 
        options=[ft.dropdown.Option(t.capitalize()) for t in dropdown_options['bodies']],
        border_radius=10,
        border_width=1
    )
    drive_wheel = ft.Dropdown(
        label="Drive Wheel", 
        options=[ft.dropdown.Option(t.upper()) for t in dropdown_options['drive_wheels']],
        border_radius=10,
        border_width=1
    )
    engine_location = ft.Dropdown(
        label="Engine Location", 
        options=[ft.dropdown.Option(t.capitalize()) for t in dropdown_options['engine_locations']],
        border_radius=10,
        border_width=1
    )
    wheel_base = create_numeric_field("Wheel Base", 86.6, 120.9, 100.0)
    car_length = create_numeric_field("Car Length", 141.1, 208.1, 175.0)
    car_width = create_numeric_field("Car Width", 60.3, 72.3, 65.0)
    car_height = create_numeric_field("Car Height", 47.8, 59.8, 55.0)
    curb_weight = create_numeric_field("Curb Weight", 1488, 4066, 2500)
    engine_type = ft.Dropdown(
        label="Engine Type", 
        options=[ft.dropdown.Option(t.upper()) for t in dropdown_options['engine_types']],
        border_radius=10,
        border_width=1
    )
    cylinders = ft.Dropdown(
        label="Cylinders", 
        options=[ft.dropdown.Option(t.capitalize()) for t in dropdown_options['cylinders']],
        border_radius=10,
        border_width=1
    )
    engine_size = create_numeric_field("Engine Size", 61, 326, 120)
    fuel_system = ft.Dropdown(
        label="Fuel System", 
        options=[ft.dropdown.Option(t.upper()) for t in dropdown_options['fuel_systems']],
        border_radius=10,
        border_width=1
    )
    bore_ratio = create_numeric_field("Bore Ratio", 2.54, 3.94, 3.2)
    stroke = create_numeric_field("Stroke", 2.07, 4.17, 3.4)
    compression = create_numeric_field("Compression", 7.0, 23.0, 9.0)
    horsepower = create_numeric_field("Horsepower", 48, 288, 100)
    peak_rpm = create_numeric_field("Peak RPM", 4150, 6600, 5000)
    city_mpg = create_numeric_field("City MPG", 13, 49, 25)
    highway_mpg = create_numeric_field("Highway MPG", 16, 54, 30)

    # Result display
    result = ft.Text("", size=24, weight="bold", text_align="center")

    def validate_input_ranges(input_data):
        ranges = {
            'symboling': (-2, 3),
            'wheel_base': (86.6, 120.9),
            'car_length': (141.1, 208.1),
            'car_width': (60.3, 72.3),
            'car_height': (47.8, 59.8),
            'curb_weight': (1488, 4066),
            'engine_size': (61, 326),
            'bore_ratio': (2.54, 3.94),
            'stroke': (2.07, 4.17),
            'compression': (7.0, 23.0),
            'horsepower': (48, 288),
            'peak_rpm': (4150, 6600),
            'city_mpg': (13, 49),
            'highway_mpg': (16, 54)
        }
        
        errors = []
        for field, (min_val, max_val) in ranges.items():
            value = float(input_data[field])
            if not (min_val <= value <= max_val):
                errors.append(f"{field.replace('_', ' ').title()} must be between {min_val} and {max_val}")
        return errors

    def predict_price(e):
        if not model_loaded:
            result.value = "Model not loaded!"
            page.update()
            return

        try:
            input_data = {
                'symboling': symboling.value,
                'fuel_type': fuel_type.value.lower(),
                'aspiration': aspiration.value.lower(),
                'doors': doors.value.lower(),
                'body': body.value.lower(),
                'drive_wheel': drive_wheel.value.lower(),
                'engine_location': engine_location.value.lower(),
                'wheel_base': wheel_base.value,
                'car_length': car_length.value,
                'car_width': car_width.value,
                'car_height': car_height.value,
                'curb_weight': curb_weight.value,
                'engine_type': engine_type.value.lower(),
                'cylinders': cylinders.value.lower(),
                'engine_size': engine_size.value,
                'fuel_system': fuel_system.value.lower(),
                'bore_ratio': bore_ratio.value,
                'stroke': stroke.value,
                'compression': compression.value,
                'horsepower': horsepower.value,
                'peak_rpm': peak_rpm.value,
                'city_mpg': city_mpg.value,
                'highway_mpg': highway_mpg.value
            }

            # Convert numeric values
            for key in ['symboling', 'wheel_base', 'car_length', 'car_width', 'car_height',
                       'curb_weight', 'engine_size', 'bore_ratio', 'stroke', 'compression',
                       'horsepower', 'peak_rpm', 'city_mpg', 'highway_mpg']:
                input_data[key] = float(input_data[key])

            # Validate ranges
            errors = validate_input_ranges(input_data)
            if errors:
                result.value = "Invalid inputs:\n" + "\n".join(errors)
                page.update()
                return

            # Prepare input DataFrame
            input_df = pd.DataFrame([input_data])
            
            # Encode categorical variables
            for col, le in encoders.items():
                if col in input_df.columns:
                    input_df[col] = le.transform(input_df[col])
            
            # Make prediction
            predicted_price = model.predict(input_df)[0]
            result.value = f"Predicted Price: ${predicted_price:,.2f}"
            
        except Exception as e:
            result.value = f"Error: {str(e)}"
        
        page.update()

    # Form sections with ExpansionTiles
    general_section = ft.ExpansionTile(
        title=ft.Text("General Info", weight="bold"),
        controls=[
            ft.Column([
                ft.Row([symboling, fuel_type], spacing=10),
                ft.Row([aspiration, doors], spacing=10)
            ])
        ]
    )

    dimensions_section = ft.ExpansionTile(
        title=ft.Text("Dimensions", weight="bold"),
        controls=[
            ft.Column([
                ft.Row([wheel_base, car_length], spacing=10),
                ft.Row([car_width, car_height], spacing=10),
                curb_weight
            ])
        ]
    )

    engine_section = ft.ExpansionTile(
        title=ft.Text("Engine Specs", weight="bold"),
        controls=[
            ft.Column([
                ft.Row([engine_type, cylinders], spacing=10),
                ft.Row([engine_size, fuel_system], spacing=10),
                ft.Row([bore_ratio, stroke], spacing=10),
                ft.Row([compression, horsepower], spacing=10)
            ])
        ]
    )

    performance_section = ft.ExpansionTile(
        title=ft.Text("Performance", weight="bold"),
        controls=[
            ft.Column([
                ft.Row([peak_rpm, city_mpg], spacing=10),
                ft.Row([highway_mpg], spacing=10)
            ])
        ]
    )

    # Predict button
    predict_button = ft.ElevatedButton(
        "PREDICT PRICE",
        on_click=predict_price,
        expand=True,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    main_container = ft.Container(
        content=ft.Column(
            [
                ft.Text("Car Price Prediction", size=24, weight="bold", text_align="center"),
                general_section,
                dimensions_section,
                engine_section,
                performance_section,
                predict_button,
                result
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            width=800  
        ),
        padding=20,
        alignment=ft.alignment.center,
    )

    page.add(
        ft.Row(
            [main_container],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
    )

if __name__ == '__main__':
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)