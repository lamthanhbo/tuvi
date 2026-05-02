from flask import Flask, render_template, request, jsonify
import requests
import random
import sqlite3
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tuvi-secret-key-2026'

GROK_API_KEY = os.getenv('GROK_API_KEY')
GROK_URL = "https://api.x.ai/v1/chat/completions"

def init_db():
    conn = sqlite3.connect('tuvi_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ten TEXT,
                    ngay_sinh TEXT,
                    gioi_tinh TEXT,
                    nam_xem INTEGER,
                    ngay_xem TEXT,
                    grok_summary TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

def save_history(ten, ngay, thang, nam, gioi_tinh, nam_xem, grok_summary):
    conn = sqlite3.connect('tuvi_history.db')
    c = conn.cursor()
    ngay_sinh = f"{ngay:02d}/{thang:02d}/{nam}"
    ngay_xem = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO history (ten, ngay_sinh, gioi_tinh, nam_xem, ngay_xem, grok_summary) VALUES (?,?,?,?,?,?)",
              (ten, ngay_sinh, gioi_tinh, nam_xem, ngay_xem, grok_summary[:500]))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect('tuvi_history.db')
    c = conn.cursor()
    c.execute("SELECT id, ten, ngay_sinh, gioi_tinh, nam_xem, ngay_xem, grok_summary FROM history ORDER BY id DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    return rows

def call_grok(prompt):
    if not GROK_API_KEY:
        return "Chưa set GROK_API_KEY. Hãy export trước khi chạy."
    headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "grok-3", "messages": [{"role": "user", "content": prompt}], "temperature": 0.75, "max_tokens": 1200}
    try:
        r = requests.post(GROK_URL, json=payload, headers=headers, timeout=20)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        return f"Lỗi API ({r.status_code})"
    except:
        return "Lỗi kết nối Grok API."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/luan-giai-tuvi', methods=['POST'])
def luan_giai():
    data = request.get_json()
    ten = data.get('ten', 'Bạn')
    ngay = data.get('ngay', 15)
    thang = data.get('thang', 5)
    nam = data.get('nam', 1995)
    gio = data.get('gio', 2)
    gioi_tinh = data.get('gioi_tinh', 'Nam')
    nam_xem = data.get('nam_xem', 2026)

    prompt = f"""Bạn là chuyên gia Tử Vi số 1 Việt Nam. Phân tích CHI TIẾT cho: {ten} ({gioi_tinh}), sinh {ngay}/{thang}/{nam} giờ {gio}h. Năm xem: {nam_xem}. Đưa ra tính cách, sự nghiệp, tình duyên, sức khỏe, vận hạn, lời khuyên cụ thể. Viết tiếng Việt ấm áp."""
    grok_analysis = call_grok(prompt)

    save_history(ten, ngay, thang, nam, gioi_tinh, nam_xem, grok_analysis)

    return jsonify({
        "can_chi": "Giáp Tý",
        "grok_full": grok_analysis,
        "quy_nhan": "Quý nhân xuất hiện mạnh",
        "cai_van": "Lời khuyên từ Grok",
        "suc_khoe": "Chú ý sức khỏe",
        "nganh_nghe": "Công nghệ, Kinh doanh",
        "van_tinh_duyen": "Rất thuận",
        "van_cong_danh": "Thăng tiến",
        "van_tai_loc": "Dồi dào",
        "van_gia_dao": "Êm ấm"
    })

@app.route('/api/history')
def history():
    return jsonify(get_history())

if __name__ == '__main__':
    app.run(debug=True, port=5000)