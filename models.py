from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symboling = db.Column(db.Integer)
    car_name = db.Column(db.String(100))
    fuel_type = db.Column(db.String(20))
    aspiration = db.Column(db.String(20))
    doors = db.Column(db.String(10))
    body = db.Column(db.String(30))
    drive_wheel = db.Column(db.String(20))
    engine_location = db.Column(db.String(20))
    wheel_base = db.Column(db.Float)
    car_length = db.Column(db.Float)
    car_width = db.Column(db.Float)
    car_height = db.Column(db.Float)
    curb_weight = db.Column(db.Integer)
    engine_type = db.Column(db.String(30))
    cylinders = db.Column(db.String(20))
    engine_size = db.Column(db.Integer)
    fuel_system = db.Column(db.String(30))
    bore_ratio = db.Column(db.Float)
    stroke = db.Column(db.Float)
    compression = db.Column(db.Float)
    horsepower = db.Column(db.Integer)
    peak_rpm = db.Column(db.Integer)
    city_mpg = db.Column(db.Integer)
    highway_mpg = db.Column(db.Integer)
    price = db.Column(db.Float)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    car_data = db.Column(db.JSON)
    predicted_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)