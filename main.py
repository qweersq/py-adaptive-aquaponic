import sqlite3
from datetime import datetime, timedelta

# Koneksi ke database
conn = sqlite3.connect('adaptiveaquaponic.db')
cursor = conn.cursor()

# Membuat tabel sensor_data jika belum ada
cursor.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ph_val REAL NOT NULL,
    humidity_val REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_sent INTEGER DEFAULT 0
)''')

# Fungsi untuk menyimpan data sensor ke database
def save_sensor_data(ph_val, humidity_val):
    cursor.execute('''INSERT INTO sensor_data (ph_val, humidity_val) VALUES (?, ?)''', (ph_val, humidity_val))
    conn.commit()

# Fungsi untuk mengirim data ke server VPS dan menandai data yang berhasil dikirim
def send_data_to_server():
    # Ambil data yang belum dikirim
    cursor.execute('''SELECT * FROM sensor_data WHERE created_at <= ? AND is_sent = 0''', (datetime.now() - timedelta(minutes=5),))
    data = cursor.fetchall()

    # Kirim data ke server VPS (contoh)
    for row in data:
        # Kode untuk mengirim data ke server VPS
        print(f"Sending data to server: {row}")

        # Update status is_sent menjadi 1 (data telah dikirim)
        cursor.execute('''UPDATE sensor_data SET is_sent = 1 WHERE id = ?''', (row[0],))
        conn.commit()

# Fungsi untuk menghapus data yang lebih dari 1 bulan
def delete_old_data():
    cursor.execute('''DELETE FROM sensor_data WHERE created_at <= ?''', (datetime.now() - timedelta(days=30),))
    conn.commit()

# Simulasi pengiriman data dan pembersihan
save_sensor_data(6.8, 70.2)  # Simulasi data sensor baru
send_data_to_server()  # Cek dan kirim data ke server (jika ada koneksi)
delete_old_data()  # Hapus data lama yang lebih dari 1 bulan

# Menutup koneksi database
cursor.close()
conn.close()
