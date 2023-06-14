import requests
import mysql.connector
import time
import sqlite3

conn = sqlite3.connect('adaptiveaquaponic.db')

cursor = conn.cursor()

# create table sensor if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ph_val REAL NOT NULL,
    humidity_val REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)'''
)

def check_internet_connection():
    try:
        response = requests.get("http://103.150.93.188:85")
        return True
    except:
        return False
    
def check_db_connection(data):
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'database': 'adaptive_aquaponic',
    }
    try:
        cnx = mysql.connector.connect(**config)
        print("Local Database Connection is available")
        cursor = cnx.cursor()
        query = ("INSERT INTO sensor_data (ph_val, humidity_val) VALUES (%s, %s)")
        cursor.execute(query, (data['ph_val'], data['humidity_val']))
        cnx.commit()
        print("Data sent to Local Database successfully")

    except:
        print("Local Database Connection is not available")
        return False
    
    finally:
        # Tutup kursor dan koneksi
        cursor.close()
        cnx.close()
    
    
def main():
    data = {
        "ph_val" : 8.0,
        "humidity_val" : 65.0,
    }
    url = "http://103.150.93.188:85/api/sensor-data"
    headers = {'Content-type': 'application/json'}
    
    if check_internet_connection():
        print("Internet connection is available")
        # send data to api
        response = requests.post(url, json=data, headers=headers)
        print(response)
        if response.status_code == 200: print("Data sent to VPS successfully")
        else : print("Data sent failed")
        
    else:
        print("Internet connection is not available")
        # send data to db mysql local
        check_db_connection(data)
        
main();