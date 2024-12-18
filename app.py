import pyrebase
from sense_emu import SenseHat
import time
import numpy as np
import sqlite3  # Import thư viện SQLite
from flask import Flask, jsonify, render_template

# Cấu hình Firebase
config = {
    "apiKey": "AIzaSyDqO65FMN9-TUdxriseZBupJjYyX09km0E",
    "authDomain": "duanio.firebaseapp.com",
    "databaseURL": "https://duanio-default-rtdb.firebaseio.com",
    "projectId": "duanio",
    "storageBucket": "duanio.firebasestorage.app",
    "messagingSenderId": "809446072915",
    "appId": "1:809446072915:web:37d287df5f8d5b11bd5ca6",
    "measurementId": "G-3ZV658YPQF"
}

# Flask app
app = Flask(__name__)

# Khởi tạo Firebase và SenseHAT
firebase = pyrebase.initialize_app(config)
database = firebase.database()
sense = SenseHat()

# Kết nối SQLite
db_file = "sensor_data.db"

def setup_sqlite():
    """Tạo bảng SensorData nếu chưa tồn tại"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS SensorData (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        temperature REAL,
                        timestamp TEXT
                      )''')
    print("Bảng SensorData đã được tạo.")                 
    conn.commit()
    conn.close()

def save_to_sql(temperature, timestamp):
    """Lưu dữ liệu nhiệt độ và thời gian vào SQLite"""
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO SensorData (temperature, timestamp) VALUES (?, ?)", 
                       (temperature, timestamp))
        conn.commit()
    except Exception as e:
        print("Lỗi khi lưu vào SQLite:", e)
    finally:
        conn.close()

# Biến toàn cục
n = 5  # Kích thước lịch sử mảng
history = [0] * n  # Mảng lịch sử
previous_T = 0  # Giá trị T trước đó
temperature_change_threshold = 1  # Ngưỡng thay đổi nhiệt độ (1 độ)

# API trả dữ liệu hiện tại
@app.route('/api/data')
def api_data():
    global history, previous_T
    current_temp = round(sense.get_temperature(), 2)
    mean_temp = np.mean(history)
    T_cap_nhat = round((current_temp + mean_temp) / 2, 2)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    if abs(current_temp - previous_T) > temperature_change_threshold:
        save_to_sql(T_cap_nhat, timestamp)
        sensor_data = {"temperature": T_cap_nhat, "timestamp": timestamp}
        database.child("OptimizedSensorData").set(sensor_data)
        previous_T = T_cap_nhat

    # Cập nhật lịch sử nhiệt độ
    history.pop(0)
    history.append(current_temp)

    return jsonify({"nhiet_do": T_cap_nhat, "do_am": round(sense.get_humidity(), 2)})

# API trả dữ liệu lịch sử
@app.route('/api/history')
def api_history():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, temperature FROM SensorData ORDER BY timestamp DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    history_data = [{"thoi_gian": row[0], "nhiet_do": row[1], "do_am": round(sense.get_humidity(), 2)} for row in rows]
    return jsonify(history_data)

# Route hiển thị file index.html
@app.route('/')
def index():
    return render_template('index.html')

# Chạy Flask Server
if __name__ == "__main__":
    print("Khởi động chương trình...")
    setup_sqlite()
    app.run(host='0.0.0.0', port=5000, debug=True)
