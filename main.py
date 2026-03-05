from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pyrebase

app = Flask(__name__)
app.secret_key = "ronen_spammer_pro_1337"

# הגדרות Firebase - מוגדר לעבוד עם הקובץ firebase_key.json שלך
config = {
    "apiKey": "AIzaSyA4ulNfLd4F19bOVsbARIVBhajnAb_96g4",
    "authDomain": "ronen-spammer-6b075.firebaseapp.com",
    "databaseURL": "https://ronen-spammer-6b075-default-rtdb.europe-west1.firebasedatabase.app",
    "storageBucket": "ronen-spammer-6b075.appspot.com",
    "serviceAccount": "firebase_key.json"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

# פונקציה שבודקת הרשאות - כאן הגדרנו אותך כמנהל
def get_user_status(email):
    if email == "afek.alfasi@gmail.com":
        return {"type": "ADMIN", "license": "LIFETIME"}
    return {"type": "USER", "license": "PENDING PURCHASE"}

@app.route('/')
def index():
    if 'user' in session:
        user_info = get_user_status(session['email'])
        return render_template('dashboard.html', user=session['email'], info=user_info)
    return redirect(url_for('login'))

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
            return "Please verify your email! Check your SPAM folder."
        except:
            return "Login failed. Check details or SPAM folder."
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.create_user_with_email_and_password(email, password)
            auth.send_email_verification(user['idToken'])
            return "Registration success! Check your SPAM folder for the link."
        except Exception as e:
            return f"Error: {str(e)}"
    return render_template('register.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        try:
            auth.send_password_reset_email(email)
            return "Password reset link sent! Check your SPAM folder."
        except:
            return "Email not found."
    return render_template('reset.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/execute_attack', methods=['POST'])
def execute_attack():
    if 'user' not in session: 
        return jsonify({"error": "Unauthorized"}), 401
    phone = request.form.get('phone')
    # בשלב הבא נוסיף כאן את רשימת ה-APIs של ה-SMS
    return jsonify({"status": "Success", "message": f"Attack on {phone} initiated!"})

if __name__ == '__main__':
    app.run()
