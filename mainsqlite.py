import sqlite3
from datetime import datetime, timedelta
import requests

conn = sqlite3.connect("adaptiveaquaponic.db")
cursor = conn.cursor()

# create table sensor if not exists
cursor.execute(
    """CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ph_val REAL NOT NULL,
    humidity_val REAL NOT NULL,
    is_sent INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)"""
)

def insert_sample_data():
    current_time = datetime.now()
    cursor.execute(
        """INSERT INTO sensor_data (ph_val, humidity_val, is_sent, created_at) VALUES (?, ?, ?, ?)""",
        (7.0, 66.0, 0, current_time),
    )
    conn.commit()
    print("Sample data inserted successfully")

def check_internet_connection():
    try:
        response = requests.get("http://103.150.93.188:85/api/sensor-data")
        if response.status_code == 200:
            return True
        return False
    except:
        return False


def send_data_to_server():
    url = "http://103.150.93.188:85/api/sensor-data"
    headers = {"Content-type": "application/json"}

    # Get data from local database is not sent
    cursor.execute(
        """SELECT * FROM sensor_data WHERE created_at >= ? AND is_sent = 0""",
        (datetime.now() - timedelta(minutes=5),),
    )
    data = cursor.fetchall()
    print(data)
    # Kirim data ke server VPS (contoh)
    for row in data:
        # Kode untuk mengirim data ke server VPS
        print(f"Sending data to server: {row}")
        payload = {
            "ph_val": row[1],
            "humidity_val": row[2],
            "created_at": row[4],
        }
        response = requests.post(url, json=payload, headers=headers)
        print(response)
        if response.status_code == 200:
            # Update status is_sent menjadi 1 (data telah dikirim)
            cursor.execute(
                """UPDATE sensor_data SET is_sent = 1 WHERE id = ?""", (row[0],)
            )
            conn.commit()
            print("Data sent to Server successfully")
        else:
            print("Data failed to send to Server")


def save_data_to_local(ph_val, humidity_val):
    current_time = datetime.now()
    cursor.execute(
        """INSERT INTO sensor_data (ph_val, humidity_val, is_sent, created_at) VALUES (?, ?, ?, ?)""",
        (ph_val, humidity_val, 0, current_time),
    )
    conn.commit()
    print("Data saved to Local Database successfully")


def delete_old_data():
    cursor.execute(
        """DELETE FROM sensor_data WHERE created_at <= ?""",
        (datetime.now() - timedelta(days=30),),
    )
    conn.commit()
    print("Data deleted from Local Database successfully")

def main():
    data = {
        "ph_val": 8.0,
        "humidity_val": 65.0,
    }
    
    save_data_to_local(data["ph_val"], data["humidity_val"])
    
    if check_internet_connection():
        print("Internet connection is available")
        send_data_to_server()
    else:
        print("Internet connection is not available")
        
    delete_old_data()
    get_all_data()

def get_all_data():
    cursor.execute("""SELECT * FROM sensor_data""")
    data = cursor.fetchall()
    print("All data")
    for row in data:
        print(row)
        
def get_data_certain_time():
    cursor.execute(
        """SELECT * FROM sensor_data WHERE created_at >= ? AND is_sent = 0""",
        (datetime.now() - timedelta(minutes=5),),
    )
    data = cursor.fetchall()
    print("5 minutes ago")
    for row in data:
        print(row)
        
def get_data_from_server():
    url = "http://103.150.93.188:85/api/sensor-data"
    headers = {"Content-type": "application/json"}
    
    response = requests.get(url, headers=headers)
    print(response.json())

# main()
# insert_sample_data()
# get_data_certain_time()
# send_data_to_server()
# get_all_data()
# get_data_from_server()

