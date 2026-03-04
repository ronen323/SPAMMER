import os
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "ronen_secret_123"

# חיבור למסד הנתונים
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://ronen-spammer-6b075-default-rtdb.europe-west1.firebasedatabase.app/'
        })
except Exception as e:
    print(f"Firebase Error: {e}")

# עיצוב האתר (HTML)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>RONEN SPAMMER</title>
    <style>
        body { background: #000; color: #ff0000; font-family: 'Courier New'; text-align: center; padding-top: 50px; }
        .box { border: 2px solid #ff0000; padding: 30px; display: inline-block; box-shadow: 0 0 20px #ff0000; }
        input { background: #111; color: #fff; border: 1px solid #ff0000; padding: 10px; margin: 10px; width: 250px; text-align: center; }
        button { background: #ff0000; color: #000; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <h1>RONEN SPAMMER</h1>
        <p>SYSTEM ONLINE</p>
        <hr style="border: 0.5px solid #333">
        <input id="key" placeholder="LICENSE KEY"><br>
        <input id="phone" placeholder="TARGET PHONE"><br>
        <button onclick="start()">EXECUTE ATTACK</button>
        <p id="msg"></p>
    </div>
    <script>
        function start() {
            alert('Attack Initiated on ' + document.getElementById('phone').value);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
