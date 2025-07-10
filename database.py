import sqlite3
from sqlite3 import Error
import pandas as pd
import os

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_tables(conn):
    """Create tables in the SQLite database"""
    try:
        cursor = conn.cursor()
        
        # Table for car brands
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS brands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """)
        
        # Table for car models
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (brand_id) REFERENCES brands (id),
            UNIQUE(brand_id, name)
        )
        """)
        
        # Table for car features and prices
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER NOT NULL,
            symboling INTEGER,
            fueltype TEXT,
            aspiration TEXT,
            doornumber TEXT,
            carbody TEXT,
            drivewheel TEXT,
            enginelocation TEXT,
            wheelbase REAL,
            carlength REAL,
            carwidth REAL,
            carheight REAL,
            curbweight INTEGER,
            enginetype TEXT,
            cylindernumber TEXT,
            enginesize INTEGER,
            fuelsystem TEXT,
            boreratio REAL,
            stroke REAL,
            compressionratio REAL,
            horsepower INTEGER,
            peakrpm INTEGER,
            citympg INTEGER,
            highwaympg INTEGER,
            price REAL,
            FOREIGN KEY (model_id) REFERENCES models (id)
        )
        """)
        
        conn.commit()
    except Error as e:
        print(e)

def populate_database(conn, csv_file):
    """Populate the database with data from CSV"""
    try:
        df = pd.read_csv(csv_file)
        
        # Extract unique brands and models
        df['brand'] = df['CarName'].apply(lambda x: x.split()[0].lower())
        df['model'] = df['CarName'].apply(lambda x: ' '.join(x.split()[1:]).lower())
        
        brands = df['brand'].unique()
        models = df[['brand', 'model']].drop_duplicates()
        
        cursor = conn.cursor()
        
        # Insert brands
        for brand in brands:
            cursor.execute("INSERT OR IGNORE INTO brands (name) VALUES (?)", (brand,))
        
        # Get brand IDs
        cursor.execute("SELECT id, name FROM brands")
        brand_ids = {name: id for id, name in cursor.fetchall()}
        
        # Insert models
        for _, row in models.iterrows():
            brand_id = brand_ids[row['brand']]
            cursor.execute(
                "INSERT OR IGNORE INTO models (brand_id, name) VALUES (?, ?)",
                (brand_id, row['model'])
            )
        
        # Get model IDs
        cursor.execute("SELECT m.id, b.name, m.name FROM models m JOIN brands b ON m.brand_id = b.id")
        model_ids = {(b_name, m_name): m_id for m_id, b_name, m_name in cursor.fetchall()}
        
        # Insert car data
        for _, row in df.iterrows():
            model_id = model_ids[(row['brand'], row['model'])]
            
            cursor.execute("""
            INSERT INTO cars (
                model_id, symboling, fueltype, aspiration, doornumber, carbody, 
                drivewheel, enginelocation, wheelbase, carlength, carwidth, 
                carheight, curbweight, enginetype, cylindernumber, enginesize, 
                fuelsystem, boreratio, stroke, compressionratio, horsepower, 
                peakrpm, citympg, highwaympg, price
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                model_id, row['symboling'], row['fueltype'], row['aspiration'], 
                row['doornumber'], row['carbody'], row['drivewheel'], 
                row['enginelocation'], row['wheelbase'], row['carlength'], 
                row['carwidth'], row['carheight'], row['curbweight'], 
                row['enginetype'], row['cylindernumber'], row['enginesize'], 
                row['fuelsystem'], row['boreratio'], row['stroke'], 
                row['compressionratio'], row['horsepower'], row['peakrpm'], 
                row['citympg'], row['highwaympg'], row['price']
            ))
        
        conn.commit()
    except Error as e:
        print(e)

def initialize_database():
    """Initialize the database with tables and data"""
    database = os.path.join('instance', 'car_data.db')
    os.makedirs('instance', exist_ok=True)
    
    conn = create_connection(database)
    if conn is not None:
        create_tables(conn)
        populate_database(conn, 'CarPrice_Assignment.csv')
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    initialize_database()