import os
import pyrebase
from flask import Flask, request, render_template_string, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "ronen_ultra_secret_99"

# הגדרות Firebase (תעתיק את אלו מה-Firebase Console -> Project Settings)
config = {
    "apiKey": "AIzaSyA4ulNfLd4F19bOVsbARIVBhajnAb_96g4",
    "authDomain": "ronen-spammer-6b075.firebaseapp.com",
    "databaseURL": "https://ronen-spammer-6b075-default-rtdb.europe-west1.firebasedatabase.app/",
    "storageBucket": "ronen-spammer-6b075.appspot.com"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

STYLE = """
<style>
    body { background: #050505; color: #ff0000; font-family: 'Segoe UI', sans-serif; text-align: center; }
    .neon-box { border: 2px solid #ff0000; padding: 40px; display: inline-block; margin-top: 50px; 
                box-shadow: 0 0 20px #ff0000; border-radius: 15px; background: #000; width: 350px; }
    input { background: #111; color: #fff; border: 1px solid #ff0000; padding: 12px; margin: 8px; width: 90%; 
            border-radius: 5px; outline: none; }
    .btn { background: #ff0000; color: #000; border: none; padding: 12px 25px; cursor: pointer; 
           font-weight: bold; border-radius: 5px; width: 95%; margin-top: 10px; }
    .msg { color: #fff; font-size: 13px; margin-top: 10px; }
    a { color: #888; text-decoration: none; font-size: 12px; }
</style>
"""

@app.route('/')
def login_page():
    return render_template_string(STYLE + """
    <div class="neon-box">
        <h1>LOGIN</h1>
        <form action="/login" method="post">
            <input name="email" type="email" placeholder="EMAIL" required><br>
            <input name="pass" type="password" placeholder="PASSWORD" required><br>
            <button class="btn">ENTER SYSTEM</button>
        </form>
        <div class="msg">{{msg}}</div>
        <br><a href="/register">NO ACCOUNT? CREATE ONE</a>
    </div>
    """, msg=request.args.get('msg', ''))

@app.route('/register')
def register_page():
    return render_template_string(STYLE + """
    <div class="neon-box">
        <h1>REGISTER</h1>
        <form action="/api/register" method="post">
            <input name="email" type="email" placeholder="EMAIL" required><br>
            <input name="pass" type="password" placeholder="PASSWORD" required><br>
            <button class="btn">CREATE & SEND VERIFICATION</button>
        </form>
        <br><a href="/">ALREADY REGISTERED? LOGIN</a>
    </div>
    """)

@app.route('/api/register', methods=['POST'])
def api_register():
    email = request.form['email']
    password = request.form['pass']
    try:
        user = auth.create_user_with_email_and_password(email, password)
        auth.send_email_verification(user['idToken'])
        return redirect(url_for('login_page', msg="Verification email sent! Check your inbox."))
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['pass']
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_info = auth.get_account_info(user['idToken'])
        
        # בדיקה אם האימייל מאומת
        if user_info['users'][0]['emailVerified']:
            session['user'] = email
            return redirect('/dashboard')
        else:
            return redirect(url_for('login_page', msg="Please verify your email first!"))
    except:
        return redirect(url_for('login_page', msg="Invalid credentials"))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect('/')
    return render_template_string(STYLE + """
    <div class="neon-box">
        <h2>SYSTEM UNLOCKED</h2>
        <p>User: {{user}}</p>
        <p style="color: yellow;">LICENSE STATUS: PENDING PURCHASE</p>
        <button class="btn" onclick="location.href='/buy'">BUY LICENSE NOW</button>
        <br><br><a href="/logout" style="color: red;">LOGOUT</a>
    </div>
    """, user=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
