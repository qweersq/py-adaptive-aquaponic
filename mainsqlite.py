import sqlite3
from datetime import datetime, timedelta
import requests

conn = sqlite3.connect("adaptiveaquaponic.db")
cursor = conn.cursor()

# create table sensor if not exists
cursor.execute(
    """CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pool_id INTEGER NOT NULL,
    temper_val REAL NOT NULL,
    ph_val REAL NOT NULL,
    humidity_val REAL NOT NULL,
    oxygen_val REAL NOT NULL,
    tds_val REAL NOT NULL,
    turbidities_val REAL NOT NULL,
    is_sent INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)"""
)


def insert_sample_data():
    current_time = datetime.now()
    cursor.execute(
        """INSERT INTO sensor_data (pool_id, temper_val, ph_val, humidity_val, oxygen_val, tds_val, turbidities_val, is_sent, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (2, 30.0, 7.0, 65.0, 5.0, 100.0, 100.0, 0, current_time),
    )
    conn.commit()
    print("Sampel data berhasil dimasukkan ke local database")


def check_internet_connection():
    try:
        print("=> Cek Koneksi ke server ...")
        response = requests.get("https://aquaponic.sinamlab.com/api/pool")
        if response.status_code == 200:
            return True
        return False
    except:
        return False


def send_data_to_server():
    url = "https://aquaponic.sinamlab.com/api/pooldata/store"
    headers = {"Content-type": "application/json"}

    # Get data from local database is not sent
    cursor.execute(
        """SELECT * FROM sensor_data WHERE created_at >= ? AND is_sent = 0""",
        (datetime.now() - timedelta(minutes=5),),
    )
    data = cursor.fetchall()
    # print(data)

    # check data if length is 5
    if len(data) < 5:
        print("=> Data kurang dari 5, tidak mengirim data ke server\n")
    else:
        # Kirim data ke server VPS (contoh)
        for row in data:
            # Kode untuk mengirim data ke server VPS
            print(f"=> Send Data : {row}")
            payload = {
                "pool_id": row[1],
                "temper_val": row[2],
                "ph_val": row[3],
                "humidity_val": row[4],
                "oxygen_val": row[5],
                "tds_val": row[6],
                "turbidities_val": row[7],
                "created_at": row[9],
            }
            response = requests.post(url, json=payload, headers=headers)
            print(response)
            if response.status_code == 200:
                # Update status is_sent menjadi 1 (data telah dikirim)
                cursor.execute(
                    """UPDATE sensor_data SET is_sent = 1 WHERE id = ?""", (row[0],)
                )
                conn.commit()
                print("=> Data berhasil dikirim ke server\n")
            else:
                print("=> Data gagal dikirim ke server\n")


def save_data_to_local(
    pool_id,
    temper_val,
    ph_val,
    humidity_val,
    oxygen_val,
    tds_val,
    turbidities_val,
    is_sent,
):
    current_time = datetime.now()
    cursor.execute(
        """INSERT INTO sensor_data (pool_id, temper_val, ph_val, humidity_val, oxygen_val, tds_val, turbidities_val, is_sent, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            pool_id,
            temper_val,
            ph_val,
            humidity_val,
            oxygen_val,
            tds_val,
            turbidities_val,
            is_sent,
            current_time,
        ),
    )
    conn.commit()
    print("=> Data tersimpan di local database\n")


def delete_old_data():
    cursor.execute(
        """DELETE FROM sensor_data WHERE created_at <= ?""",
        (datetime.now() - timedelta(days=30),),
    )
    conn.commit()
    print("=> Menghapus data satu bulan lalu berhasil\n")


def main():
    while True:
        # program dibawah akan dijalankan ketika satu menit sekali
        now = datetime.now()
        if now.second == 0 and now.microsecond == 0:
            data = {
                "pool_id": 2,
                "temper_val": 25.39,
                "ph_val": 7.2,
                "humidity_val": 40.0,
                "oxygen_val": 4.2,
                "tds_val": 1693,
                "turbidities_val": 1988.11,
                "is_sent": 0,
            }

            save_data_to_local(
                data["pool_id"],
                data["temper_val"],
                data["ph_val"],
                data["humidity_val"],
                data["oxygen_val"],
                data["tds_val"],
                data["turbidities_val"],
                data["is_sent"],
            )

            if check_internet_connection():
                print("=> Terhubung ke server\n")
                send_data_to_server()
            else:
                print("=> Tidak terhubung ke server")
                print("=> Data telah tersimpan di local database\n")

            delete_old_data()
            get_all_data()


def get_all_data():
    cursor.execute("""SELECT * FROM sensor_data""")
    data = cursor.fetchall()
    print("\nSemua Data di local database")
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
    url = "https://aquaponic.sinamlab.com/api/pooldata"
    headers = {"Content-type": "application/json"}

    response = requests.get(url, headers=headers)
    print(response.json())


main()
# check_internet_connection()
# insert_sample_data()
# get_data_certain_time()
# send_data_to_server()
# delete_old_data()
# get_all_data()
# get_data_from_server()
