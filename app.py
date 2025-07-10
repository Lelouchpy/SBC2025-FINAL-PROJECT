import os
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Car, User, Prediction
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error
import joblib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_price.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db.init_app(app)

def validate_input_ranges(form_data):
    """Validate that numeric inputs are within dataset ranges"""
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
        value = float(form_data[field])
        if not (min_val <= value <= max_val):
            errors.append(f"{field.replace('_', ' ').title()} must be between {min_val} and {max_val}")
    
    return errors

# Create database tables
with app.app_context():
    db.create_all()

# Load and preprocess data
def load_data():
    # Check if data already exists in database
    if Car.query.count() == 0:
        df = pd.read_csv('CarPrice_Assignment.csv')
        
        # Clean and prepare data
        df = df.dropna()
        df = df.drop_duplicates()
        
        # Save to database
        for _, row in df.iterrows():
            car = Car(
                symboling=row['symboling'],
                car_name=row['CarName'],
                fuel_type=row['fueltype'],
                aspiration=row['aspiration'],
                doors=row['doornumber'],
                body=row['carbody'],
                drive_wheel=row['drivewheel'],
                engine_location=row['enginelocation'],
                wheel_base=row['wheelbase'],
                car_length=row['carlength'],
                car_width=row['carwidth'],
                car_height=row['carheight'],
                curb_weight=row['curbweight'],
                engine_type=row['enginetype'],
                cylinders=row['cylindernumber'],
                engine_size=row['enginesize'],
                fuel_system=row['fuelsystem'],
                bore_ratio=row['boreratio'],
                stroke=row['stroke'],
                compression=row['compressionratio'],
                horsepower=row['horsepower'],
                peak_rpm=row['peakrpm'],
                city_mpg=row['citympg'],
                highway_mpg=row['highwaympg'],
                price=row['price']
            )
            db.session.add(car)
        db.session.commit()
    
    # Query data from database
    cars = Car.query.all()
    data = {
        'symboling': [car.symboling for car in cars],
        'fuel_type': [car.fuel_type for car in cars],
        'aspiration': [car.aspiration for car in cars],
        'doors': [car.doors for car in cars],
        'body': [car.body for car in cars],
        'drive_wheel': [car.drive_wheel for car in cars],
        'engine_location': [car.engine_location for car in cars],
        'wheel_base': [car.wheel_base for car in cars],
        'car_length': [car.car_length for car in cars],
        'car_width': [car.car_width for car in cars],
        'car_height': [car.car_height for car in cars],
        'curb_weight': [car.curb_weight for car in cars],
        'engine_type': [car.engine_type for car in cars],
        'cylinders': [car.cylinders for car in cars],
        'engine_size': [car.engine_size for car in cars],
        'fuel_system': [car.fuel_system for car in cars],
        'bore_ratio': [car.bore_ratio for car in cars],
        'stroke': [car.stroke for car in cars],
        'compression': [car.compression for car in cars],
        'horsepower': [car.horsepower for car in cars],
        'peak_rpm': [car.peak_rpm for car in cars],
        'city_mpg': [car.city_mpg for car in cars],
        'highway_mpg': [car.highway_mpg for car in cars],
        'price': [car.price for car in cars]
    }
    
    return pd.DataFrame(data)

# Train or load model
def get_model():
    model_path = 'car_price_model.pkl'
    if os.path.exists(model_path):
        return joblib.load(model_path)
    else:
        df = load_data()
        
        # Encode categorical variables
        categorical_cols = ['fuel_type', 'aspiration', 'doors', 'body', 'drive_wheel', 
                          'engine_location', 'engine_type', 'cylinders', 'fuel_system']
        label_encoders = {}
        for col in categorical_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            label_encoders[col] = le
        
        # Features and target
        X = df.drop('price', axis=1)
        y = df['price']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        print(f"Model trained with MAE: ${mae:.2f}")
        
        # Save model and encoders
        joblib.dump({
            'model': model,
            'encoders': label_encoders
        }, model_path)
        
        return {'model': model, 'encoders': label_encoders}

# Get unique values for dropdowns
def get_dropdown_values():
    df = load_data()
    return {
        'fuel_types': sorted(df['fuel_type'].unique()),
        'aspirations': sorted(df['aspiration'].unique()),
        'doors': sorted(df['doors'].unique()),
        'bodies': sorted(df['body'].unique()),
        'drive_wheels': sorted(df['drive_wheel'].unique()),
        'engine_locations': sorted(df['engine_location'].unique()),
        'engine_types': sorted(df['engine_type'].unique()),
        'cylinders': sorted(df['cylinders'].unique()),
        'fuel_systems': sorted(df['fuel_system'].unique())
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    dropdown_values = get_dropdown_values()
    
    if request.method == 'POST':
        # Get form data
        form_data = {
            'symboling': int(request.form['symboling']),
            'fuel_type': request.form['fuel_type'],
            'aspiration': request.form['aspiration'],
            'doors': request.form['doors'],
            'body': request.form['body'],
            'drive_wheel': request.form['drive_wheel'],
            'engine_location': request.form['engine_location'],
            'wheel_base': float(request.form['wheel_base']),
            'car_length': float(request.form['car_length']),
            'car_width': float(request.form['car_width']),
            'car_height': float(request.form['car_height']),
            'curb_weight': int(request.form['curb_weight']),
            'engine_type': request.form['engine_type'],
            'cylinders': request.form['cylinders'],
            'engine_size': int(request.form['engine_size']),
            'fuel_system': request.form['fuel_system'],
            'bore_ratio': float(request.form['bore_ratio']),
            'stroke': float(request.form['stroke']),
            'compression': float(request.form['compression']),
            'horsepower': int(request.form['horsepower']),
            'peak_rpm': int(request.form['peak_rpm']),
            'city_mpg': int(request.form['city_mpg']),
            'highway_mpg': int(request.form['highway_mpg'])
        }
        
        # Validate ranges
        errors = validate_input_ranges(form_data)
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('predict.html', dropdown_values=dropdown_values)
        
        # Load model
        model_data = get_model()
        model = model_data['model']
        encoders = model_data['encoders']
        
        # Prepare input data
        input_df = pd.DataFrame([form_data])
        
        # Encode categorical variables
        for col, le in encoders.items():
            input_df[col] = le.transform(input_df[col])
        
        # Make prediction
        predicted_price = model.predict(input_df)[0]
        
        # For demo purposes, create a dummy user
        user = User.query.filter_by(username='demo').first()
        if not user:
            user = User(username='demo', email='demo@example.com')
            db.session.add(user)
            db.session.commit()
        
        # Save prediction to database
        prediction = Prediction(
            user_id=user.id,
            car_data=form_data,
            predicted_price=predicted_price
        )
        db.session.add(prediction)
        db.session.commit()
        
        return render_template('results.html', 
                             form_data=form_data,
                             predicted_price=round(predicted_price, 2))
    
    return render_template('predict.html', dropdown_values=dropdown_values)

if __name__ == '__main__':
    app.run(debug=True)