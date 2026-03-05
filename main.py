from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pyrebase
import requests

app = Flask(__name__)
app.secret_key = "ronen_spammer_ultimate_secret"

# הגדרות ה-Firebase שלך - מעודכן לפי מה שעבד לנו
config = {
    "apiKey": "AIzaSyA4ulNfLd4F19bOVsbARIVBhajnAb_96g4",
    "authDomain": "ronen-spammer-6b075.firebaseapp.com",
    "databaseURL": "https://ronen-spammer-6b075-default-rtdb.europe-west1.firebasedatabase.app",
    "storageBucket": "ronen-spammer-6b075.appspot.com",
    "serviceAccount": "firebase_key.json" # שים פה את השם המדויק של הקובץ
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

# פונקציית עזר לבדיקת הרשאות
def get_user_status(email):
    # הגדרת ה-Admin הראשי
    if email == "afek.alfasi@gmail.com":
        return {"type": "ADMIN", "license": "LIFETIME", "status": "ACTIVE"}
    return {"type": "USER", "license": "PENDING", "status": "LOCKED"}

@app.route('/')
def index():
    if 'user' in session:
        user_info = get_user_status(session['email'])
        return render_template('dashboard.html', user=session['email'], info=user_info)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.create_user_with_email_and_password(email, password)
            auth.send_email_verification(user['idToken'])
            return "Registration successful! **Check your SPAM FOLDER** for the verification link."
        except Exception as e:
            return f"Error: {str(e)}"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            info = auth.get_account_info(user['idToken'])
            if info['users'][0]['emailVerified']:
                session['user'] = user['idToken']
                session['email'] = email
                return redirect(url_for('index'))
            else:
                return "Please verify your email first. **Check your SPAM FOLDER!**"
        except:
            return "Login failed. Check details or your Spam folder for verification."
    return render_template('login.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        try:
            auth.send_password_reset_email(email)
            return "Reset link sent! **Check your SPAM FOLDER**."
        except:
            return "Email not found."
    return render_template('reset.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# לוגיקת המתקפה (השלב הבא)
@app.route('/execute_attack', methods=['POST'])
def execute_attack():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_info = get_user_status(session['email'])
    if user_info['license'] != "LIFETIME":
        return jsonify({"error": "License required"}), 403

    target = request.form.get('phone')
    # כאן נכניס את רשימת ה-API של ה-SMS בשלב הבא
    print(f"Attack started on {target} by {session['email']}")
    return jsonify({"status": "Attack Sent", "target": target})

if __name__ == '__main__':
    app.run(debug=True)
