from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import openai
from ai.recommender import get_ai_recommendations
from datetime import date
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = 'secret_key_fitmind'  # Replace with strong secret for production
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# MySQL DB configuration (update your credentials)
db_config = {
    'host': 'localhost',
    'user': 'your_mysql_username',
    'password': 'your_mysql_password',
    'database': 'fitmind_db'
}

# OpenAI API Key (replace with your real key)
openai.api_key = 'YOUR_OPENAI_API_KEY'


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = generate_password_hash(request.form['password'])

    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return redirect('/')
    except mysql.connector.errors.IntegrityError:
        return render_template('index.html', error="Username already exists.")
    finally:
        cur.close()
        conn.close()


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect('/dashboard')
    return render_template('index.html', error="Invalid credentials.")


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('dashboard.html', username=session['username'])


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/')

    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)

    if request.method == 'POST':
        age = request.form['age']
        gender = request.form['gender']
        weight = request.form['weight']
        goals = request.form['goals']
        cur.execute(
            "UPDATE users SET age=%s, gender=%s, weight=%s, goals=%s WHERE id=%s",
            (age, gender, weight, goals, session['user_id'])
        )
        conn.commit()

    cur.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('profile.html', user=user)


@app.route('/log', methods=['POST'])
def log():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO logs (user_id, date, steps, calories, heart_rate, sleep_hours, mood, hydration)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        session['user_id'], data.get('date', str(date.today())),
        data['steps'], data['calories'], data['heart_rate'],
        data['sleep_hours'], data['mood'], data['hydration']
    ))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'success': True})


@app.route('/logs')
def logs():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT date, steps, calories, heart_rate, sleep_hours, mood, hydration
        FROM logs WHERE user_id=%s ORDER BY date ASC
    """, (session['user_id'],))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)


@app.route('/recommendations', methods=['POST'])
def recommendations():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(get_ai_recommendations(user))


@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get('message', '')
    if not msg:
        return jsonify({'reply': 'Please type something so I can help you!'})

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": "You are a helpful AI fitness coach."},
            {"role": "user", "content": msg}
        ],
        max_tokens=200,
        temperature=0.7,
    )
    reply = response['choices'][0]['message']['content']
    return jsonify({'reply': reply})


@app.route('/export/csv')
def export_csv():
    if 'user_id' not in session:
        return redirect('/')
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""
        SELECT date, steps, calories, heart_rate, sleep_hours, mood, hydration
        FROM logs WHERE user_id=%s ORDER BY date
    """, (session['user_id'],))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Steps', 'Calories', 'Heart Rate', 'Sleep Hours', 'Mood', 'Hydration'])
    writer.writerows(rows)

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=logs.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response


if __name__ == '__main__':
    app.run(debug=True)
