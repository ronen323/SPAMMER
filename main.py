import os
from flask import Flask, request, render_template_string, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "ronen_vault_777"

# עיצוב CSS גלובלי לכל האתר (ניאון האקרי)
STYLE = """
<style>
    body { background: #050505; color: #ff0000; font-family: 'Segoe UI', sans-serif; text-align: center; }
    .neon-box { border: 2px solid #ff0000; padding: 40px; display: inline-block; margin-top: 50px; 
                box-shadow: 0 0 20px #ff0000, inset 0 0 10px #ff0000; border-radius: 15px; background: #000; }
    input { background: #111; color: #fff; border: 1px solid #ff0000; padding: 15px; margin: 10px; width: 300px; 
            border-radius: 5px; font-size: 16px; outline: none; }
    .btn { background: #ff0000; color: #000; border: none; padding: 15px 30px; cursor: pointer; 
           font-weight: bold; border-radius: 5px; font-size: 18px; text-transform: uppercase; transition: 0.3s; }
    .btn:hover { background: #fff; box-shadow: 0 0 20px #fff; }
    .pricing { display: flex; gap: 20px; justify-content: center; margin-top: 30px; }
    .plan { border: 1px solid #444; padding: 20px; border-radius: 10px; width: 150px; }
    .plan h3 { margin: 0; color: #fff; }
    a { color: #888; text-decoration: none; font-size: 14px; }
</style>
"""

@app.route('/')
def login_page():
    return render_template_string(STYLE + """
    <div class="neon-box">
        <h1 style="font-size: 40px; letter-spacing: 5px;">RONEN SPAMMER</h1>
        <p style="color: #555;">SECURE ACCESS SYSTEM</p>
        <form action="/login" method="post">
            <input name="u" placeholder="USERNAME" required><br>
            <input name="p" type="password" placeholder="PASSWORD" required><br>
            <button class="btn">ENTER SYSTEM</button>
        </form>
        <br><a href="/pricing">DON'T HAVE AN ACCOUNT? VIEW PRICING</a>
    </div>
    """)

@app.route('/pricing')
def pricing():
    return render_template_string(STYLE + """
    <div class="neon-box" style="width: 800px;">
        <h1>SYSTEM PRICING</h1>
        <div class="pricing">
            <div class="plan"><h3>DAILY</h3><p>15 ILS</p></div>
            <div class="plan" style="border-color: #ff0000;"><h3>MONTHLY</h3><p>50 ILS</p></div>
            <div class="plan"><h3>LIFETIME</h3><p>200 ILS</p></div>
        </div>
        <br><br>
        <button class="btn" onclick="alert('Redirecting to Sellix...')">BUY LICENSE KEY</button>
        <br><br><a href="/">ALREADY HAVE AN ACCOUNT? LOGIN</a>
    </div>
    """)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect('/')
    return render_template_string(STYLE + """
    <div class="neon-box">
        <h2>WELCOME, {{user}}</h2>
        <p style="color: #0f0;">STATUS: ACTIVE LICENSE</p>
        <hr style="border: 0.5px solid #222">
        <input id="target" placeholder="TARGET PHONE (05XXXXXXXX)">
        <br><button class="btn">EXECUTE ATTACK</button>
        <br><br><a href="/logout" style="color: red;">LOGOUT</a>
    </div>
    """, user=session['user'])

@app.route('/login', methods=['POST'])
def login():
    session['user'] = request.form['u']
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
