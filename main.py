from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
import requests
import threading
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.secret_key = "ronen_secret_key_123" # תשנה למשהו סודי

# --- חיבור ל-Firebase ---
# וודא שיש לך קובץ בשם firebase_key.json באותה תיקייה
try:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://ronen-spammer-6b075-default-rtdb.europe-west1.firebasedatabase.app/'
    })
except:
    print("Firebase Error: Make sure firebase_key.json exists!")

# --- Helper Functions ---
def get_user_data(username):
    return db.reference(f'users/{username}').get()

def update_user_time(username, days):
    ref = db.reference(f'users/{username}')
    data = ref.get()
    current_expiry = data.get('expiry', datetime.now().strftime("%Y-%m-%d"))
    
    if current_expiry == "lifetime": return
    
    start_dt = max(datetime.now(), datetime.strptime(current_expiry, "%Y-%m-%d"))
    new_expiry = (start_dt + timedelta(days=days)).strftime("%Y-%m-%d")
    ref.update({'expiry': new_expiry})

# --- HTML Templates (Hacker Style) ---
BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>RONEN SPAMMER | SYSTEM</title>
    <style>
        body { background: #000; color: #ff0000; font-family: 'Courier New'; text-align: center; }
        .container { border: 2px solid #ff0000; padding: 20px; display: inline-block; margin-top: 50px; box-shadow: 0 0 20px #ff0000; }
        input { background: #111; color: #fff; border: 1px solid #ff0000; padding: 10px; margin: 5px; width: 200px; }
        button { background: #ff0000; color: #000; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; }
        .nav { margin-bottom: 20px; }
        a { color: #fff; text-decoration: none; margin: 0 10px; }
    </style>
</head>
<body>
    <div class="container">
        {% if session.get('user') %}
            <div class="nav">
                <span>User: {{ session['user'] }}</span> | 
                <a href="/logout">Logout</a>
            </div>
        {% endif %}
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    if 'user' in session: return redirect(url_for('dashboard'))
    return render_template_string(BASE_HTML + """
    {% block content %}
    <h1>LOGIN TO SYSTEM</h1>
    <form action="/login" method="post">
        <input name="username" placeholder="Username" required><br>
        <input name="password" type="password" placeholder="Password" required><br>
        <button type="submit">ENTER</button>
    </form>
    <p>Don't have an account? <a href="/register">Register</a></p>
    {% endblock %}
    """)

@app.route('/register')
def register_page():
    return render_template_string(BASE_HTML + """
    {% block content %}
    <h1>CREATE ACCOUNT</h1>
    <form action="/api/register" method="post">
        <input name="username" placeholder="Username" required><br>
        <input name="password" type="password" placeholder="Password" required><br>
        <button type="submit">CREATE</button>
    </form>
    {% endblock %}
    """)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('home'))
    user_data = get_user_data(session['user'])
    return render_template_string(BASE_HTML + """
    {% block content %}
    <h1>DASHBOARD</h1>
    <p>Expiry Date: <span style="color:white">{{ expiry }}</span></p>
    <hr style="border:1px solid #ff0000">
    <h3>REDEEM KEY</h3>
    <input id="key_input" placeholder="XXXX-XXXX-XXXX">
    <button onclick="redeem()">ACTIVATE</button>
    <hr style="border:1px solid #ff0000">
    <h3>LAUNCH ATTACK</h3>
    <input id="target" placeholder="05XXXXXXXX">
    <button onclick="attack()" style="background:white; color:red;">START SPAM</button>
    
    <script>
        function redeem() {
            const key = document.getElementById('key_input').value;
            fetch('/api/redeem', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: key})
            }).then(r => r.json()).then(d => { alert(d.message); location.reload(); });
        }
        function attack() {
            const phone = document.getElementById('target').value;
            fetch('/api/attack', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({phone: phone})
            }).then(r => r.json()).then(d => alert(d.message));
        }
    </script>
    {% endblock %}
    """, expiry=user_data.get('expiry', 'Expired'))

# --- API Routes ---

@app.route('/login', methods=['POST'])
def login():
    u = request.form['username']
    p = request.form['password']
    data = get_user_data(u)
    if data and data.get('password') == p:
        session['user'] = u
        return redirect(url_for('dashboard'))
    return "Invalid Credentials"

@app.route('/api/register', methods=['POST'])
def api_register():
    u = request.form['username']
    p = request.form['password']
    if get_user_data(u): return "User exists"
    db.reference(f'users/{u}').set({
        'password': p,
        'expiry': datetime.now().strftime("%Y-%m-%d")
    })
    return redirect(url_for('home'))

@app.route('/api/redeem', methods=['POST'])
def api_redeem():
    if 'user' not in session: return jsonify({"message": "Unauthorized"}), 401
    k = request.json.get('key')
    key_ref = db.reference(f'keys/{k}')
    key_data = key_ref.get()
    
    if not key_data: return jsonify({"message": "Invalid Key"}), 404
    
    days = key_data.get('days', 0)
    if days == -1: # Lifetime logic
        db.reference(f'users/{session["user"]}').update({'expiry': 'lifetime'})
    else:
        update_user_time(session['user'], days)
    
    key_ref.delete() # מפתח חד פעמי
    return jsonify({"message": f"Successfully added {days} days!"})

@app.route('/api/attack', methods=['POST'])
def api_attack():
    if 'user' not in session: return jsonify({"message": "Login first"}), 401
    user_data = get_user_data(session['user'])
    # כאן תוסיף בדיקה אם התוקף פג
    
    phone = request.json.get('phone')
    # כאן תפעיל את ה-ThreadPool של הספאם מהקוד הקודם שלך
    return jsonify({"message": "Attack Dispatched to Cloud!"})

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
