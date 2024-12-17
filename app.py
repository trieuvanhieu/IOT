from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sense_emu import SenseHat
import firebase_admin
from firebase_admin import credentials, db
import time

# Khởi tạo Sense HAT và Flask
cam_bien = SenseHat()
app = Flask(__name__)

# Cấu hình SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db_sql = SQLAlchemy(app)

# Firebase cấu hình (tải tệp JSON từ Firebase)
cred = credentials.Certificate("firebase_credentials.json")  # Thay bằng tệp của bạn
firebase_admin.initialize_app(cred, {'databaseURL': 'https://your-firebase-url.firebaseio.com'})

# Định nghĩa bảng dữ liệu
class DuLieuCamBien(db_sql.Model):
    id = db_sql.Column(db_sql.Integer, primary_key=True)
    nhiet_do = db_sql.Column(db_sql.Float, nullable=False)
    do_am = db_sql.Column(db_sql.Float, nullable=False)
    thoi_gian = db_sql.Column(db_sql.String(50), nullable=False)

# Hàm đọc dữ liệu cảm biến
def doc_du_lieu_cam_bien():
    nhiet_do = round(cam_bien.get_temperature(), 1)
    do_am = round(cam_bien.get_humidity(), 1)
    return {"nhiet_do": nhiet_do, "do_am": do_am, "thoi_gian": time.strftime('%Y-%m-%d %H:%M:%S')}

# Route trang chủ
@app.route("/")
def index():
    return render_template("index.html")

# API lấy và lưu dữ liệu vào SQL và Firebase
@app.route("/api/data")
def api_data():
    data = doc_du_lieu_cam_bien()
    
    # Lưu vào SQLite
    du_lieu = DuLieuCamBien(nhiet_do=data['nhiet_do'], do_am=data['do_am'], thoi_gian=data['thoi_gian'])
    db_sql.session.add(du_lieu)
    db_sql.session.commit()
    
    # Đẩy dữ liệu lên Firebase
    ref = db.reference('du_lieu_cam_bien')
    ref.push(data)
    
    return jsonify(data)

# Route xem lịch sử dữ liệu từ SQL
@app.route("/api/history")
def xem_lich_su():
    lich_su = DuLieuCamBien.query.all()
    data = [{"nhiet_do": d.nhiet_do, "do_am": d.do_am, "thoi_gian": d.thoi_gian} for d in lich_su]
    return jsonify(data)

# Khởi tạo database (chỉ cần chạy 1 lần)
@app.before_first_request
def create_tables():
    db_sql.create_all()

# Chạy ứng dụng Flask
if __name__ == "__main__":
    app.run(debug=True)
