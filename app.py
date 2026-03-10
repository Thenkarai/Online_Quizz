import os
import sqlite3
import random
import string
import json
import qrcode
import csv
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import io

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_quiz_app'

# Serverless Read-Only Filesystem Fixes (Vercel & Netlify)
if os.environ.get('VERCEL') == '1' or os.environ.get('NETLIFY') == 'true' or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    DATABASE = '/tmp/quiz_system.db'
    QR_DIR = '/tmp/qrcodes'
    UPLOAD_DIR = '/tmp/uploads'
else:
    DATABASE = 'quiz_system.db'
    QR_DIR = os.path.join('static', 'qrcodes')
    UPLOAD_DIR = os.path.join('static', 'uploads')

@app.template_filter('from_json')
def from_json_filter(value):
    return json.loads(value)

# --- Database Helpers ---

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    if not os.path.exists(DATABASE):
        with app.app_context():
            db = get_db()
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r') as f:
                db.cursor().executescript(f.read())
            # Default admin
            db.execute("INSERT INTO admins (username, password) VALUES (?, ?)",
                       ('admin1@gmail.com', generate_password_hash('Admin.123')))
            db.commit()

# --- Routes ---

@app.route('/')
def index():
    return render_template('home.html')

# --- Admin Routes ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        admin = db.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
        if admin and check_password_hash(admin['password'], password):
            session['admin_id'] = admin['id']
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    db = get_db()
    quizzes = db.execute("SELECT * FROM quizzes ORDER BY created_at DESC").fetchall()
    return render_template('admin_dashboard.html', quizzes=quizzes)

@app.route('/admin/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        title = request.form['title']
        duration = request.form['duration']
        num_questions = request.form['num_questions']
        time_per_q = request.form.get('time_per_question', 30)
        quiz_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        db = get_db()
        db.execute("INSERT INTO quizzes (title, duration, num_questions, quiz_code, time_per_question, admin_id) VALUES (?, ?, ?, ?, ?, ?)",
                   (title, duration, num_questions, quiz_code, time_per_q, session['admin_id']))
        db.commit()
        
        # Generate QR Code
        join_url = f"{request.host_url}participant/join?code={quiz_code}"
        qr = qrcode.make(join_url)
        if not os.path.exists(QR_DIR):
            os.makedirs(QR_DIR)
        qr.save(os.path.join(QR_DIR, f"{quiz_code}.png"))
        
        return redirect(url_for('add_questions', quiz_id=db.execute("SELECT last_insert_rowid()").fetchone()[0]))
    return render_template('create_quiz.html')

@app.route('/admin/add_questions/<int:quiz_id>', methods=['GET', 'POST'])
def add_questions(quiz_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    db = get_db()
    quiz = db.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    if request.method == 'POST':
        q_text = request.form['question_text']
        q_type = request.form['question_type']
        correct = request.form['correct_answer']
        options = None
        image_path = None
        
        if q_type in ['mcq', 'image']:
            opts = [request.form['opt1'], request.form['opt2'], request.form['opt3'], request.form['opt4']]
            options = json.dumps(opts)
        
        if q_type == 'image':
            file = request.files['image_file']
            if file:
                if not os.path.exists(UPLOAD_DIR):
                    os.makedirs(UPLOAD_DIR)
                image_filename = f"{datetime.now().timestamp()}_{file.filename}"
                image_path = f"uploads/{image_filename}"
                file.save(os.path.join(UPLOAD_DIR, image_filename))
        
        db.execute("INSERT INTO questions (quiz_id, question_text, question_type, options, correct_answer, image_path) VALUES (?, ?, ?, ?, ?, ?)",
                   (quiz_id, q_text, q_type, options, correct, image_path))
        db.commit()
        
        current_count = db.execute("SELECT COUNT(*) FROM questions WHERE quiz_id = ?", (quiz_id,)).fetchone()[0]
        if current_count >= quiz['num_questions']:
            return redirect(url_for('admin_dashboard'))
    
    return render_template('add_questions.html', quiz=quiz)

# --- Participant Routes ---

@app.route('/participant/join', methods=['GET', 'POST'])
def participant_join():
    code = request.args.get('code', '')
    if request.method == 'POST':
        quiz_code = request.form['quiz_code']
        name = request.form['name']
        reg_num = request.form['reg_num']
        
        db = get_db()
        quiz = db.execute("SELECT * FROM quizzes WHERE quiz_code = ?", (quiz_code.upper(),)).fetchone()
        if quiz:
            cursor = db.execute("INSERT INTO participants (name, register_number, quiz_id, status) VALUES (?, ?, ?, 'pending')",
                       (name, reg_num, quiz['id']))
            db.commit()
            session['participant_id'] = cursor.lastrowid
            session['quiz_id'] = quiz['id']
            return redirect(url_for('waiting_room'))
        flash('Invalid Quiz Code', 'danger')
    return render_template('join_quiz.html', code=code)

@app.route('/participant/waiting_room')
def waiting_room():
    if 'participant_id' not in session:
        return redirect(url_for('participant_join'))
    return render_template('waiting_room.html')

@app.route('/api/check_status')
def check_status():
    p_id = session.get('participant_id')
    if not p_id: return jsonify({'status': 'unauthorized'})
    db = get_db()
    participant = db.execute("SELECT status FROM participants WHERE id = ?", (p_id,)).fetchone()
    return jsonify({'status': participant['status']})

@app.route('/participant/quiz')
def quiz_page():
    if 'participant_id' not in session:
        return redirect(url_for('participant_join'))
    db = get_db()
    quiz = db.execute("SELECT * FROM quizzes WHERE id = ?", (session['quiz_id'],)).fetchone()
    questions = db.execute("SELECT * FROM questions WHERE quiz_id = ?", (session['quiz_id'],)).fetchall()
    
    # Check if already submitted or not yet approved
    participant = db.execute("SELECT status FROM participants WHERE id = ?", (session['participant_id'],)).fetchone()
    if participant['status'] in ['pending', 'joined']:
        return redirect(url_for('waiting_room'))
    if participant['status'] == 'submitted':
        return redirect(url_for('results'))
    
    if participant['status'] == 'approved':
        db.execute("UPDATE participants SET status = 'started' WHERE id = ?", (session['participant_id'],))
        db.commit()
        
    return render_template('quiz_interface.html', quiz=quiz, questions=questions)

@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    data = request.json
    p_id = session.get('participant_id')
    if not p_id: return jsonify({'error': 'Unauthorized'}), 401
    
    db = get_db()
    q_id = data['question_id']
    ans = data['answer']
    
    question = db.execute("SELECT correct_answer FROM questions WHERE id = ?", (q_id,)).fetchone()
    is_correct = (str(ans).strip().lower() == str(question['correct_answer']).strip().lower())
    
    db.execute("DELETE FROM answers WHERE participant_id = ? AND question_id = ?", (p_id, q_id))
    db.execute("INSERT INTO answers (participant_id, question_id, submitted_answer, is_correct) VALUES (?, ?, ?, ?)",
               (p_id, q_id, ans, is_correct))
    db.commit()
    return jsonify({'success': True})

@app.route('/api/finish_quiz', methods=['POST'])
def finish_quiz():
    data = request.json
    p_id = session.get('participant_id')
    if not p_id: return jsonify({'error': 'Unauthorized'}), 401
    
    db = get_db()
    p_id = session['participant_id']
    quiz_id = session['quiz_id']
    
    # Calculate score
    score_data = db.execute("SELECT COUNT(*) FROM answers WHERE participant_id = ? AND is_correct = 1", (p_id,)).fetchone()
    score = score_data[0]
    total = db.execute("SELECT num_questions FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()[0]
    
    db.execute("UPDATE participants SET status = 'submitted' WHERE id = ?", (p_id,))
    db.execute("INSERT INTO results (participant_id, score, total_questions, time_taken, cheating_warnings) VALUES (?, ?, ?, ?, ?)",
               (p_id, score, total, data.get('time_taken', 0), data.get('warnings', 0)))
    db.commit()
    return jsonify({'success': True})

@app.route('/api/suspend_participant', methods=['POST'])
def suspend_participant():
    p_id = session.get('participant_id')
    if not p_id: return jsonify({'error': 'Unauthorized'}), 401
    
    db = get_db()
    db.execute("UPDATE participants SET status = 'pending' WHERE id = ?", (p_id,))
    db.commit()
    return jsonify({'success': True})

@app.route('/participant/results')
def results():
    if 'participant_id' not in session:
        return redirect(url_for('participant_join'))
    db = get_db()
    res = db.execute("SELECT * FROM results WHERE participant_id = ?", (session['participant_id'],)).fetchone()
    
    # Leaderboard
    leaderboard = db.execute("""
        SELECT p.name, r.score, r.time_taken 
        FROM results r 
        JOIN participants p ON r.participant_id = p.id 
        WHERE p.quiz_id = ?
        ORDER BY r.score DESC, r.time_taken ASC
    """, (session['quiz_id'],)).fetchall()
    
    return render_template('results.html', results=res) # Removed leaderboard for participants

@app.route('/admin/quiz_view/<int:quiz_id>')
def admin_quiz_view(quiz_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    db = get_db()
    quiz = db.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    pending = db.execute("SELECT * FROM participants WHERE quiz_id = ? AND status IN ('pending', 'joined')", (quiz_id,)).fetchall()
    
    # Leaderboard with Risk Score
    leaderboard = db.execute("""
        SELECT p.name, r.score, r.time_taken, r.cheating_warnings,
               (r.cheating_warnings * 33) as risk_score
        FROM results r 
        JOIN participants p ON r.participant_id = p.id 
        WHERE p.quiz_id = ?
        ORDER BY r.score DESC, r.time_taken ASC
    """, (quiz_id,)).fetchall()
    
    # Suspicious Activity Log
    cheating_logs = db.execute("""
        SELECT p.name, c.event_type, c.timestamp
        FROM cheating_logs c
        JOIN participants p ON c.participant_id = p.id
        WHERE p.quiz_id = ?
        ORDER BY c.timestamp DESC
        LIMIT 20
    """, (quiz_id,)).fetchall()
    
    return render_template('admin_quiz_view.html', quiz=quiz, pending=pending, leaderboard=leaderboard, cheating_logs=cheating_logs)

@app.route('/api/approve_participant/<int:p_id>', methods=['POST'])
def approve_participant(p_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    db.execute("UPDATE participants SET status = 'approved' WHERE id = ?", (p_id,))
    db.commit()
    return jsonify({'success': True})
@app.route('/admin/export/<int:quiz_id>')
def export_results(quiz_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    db = get_db()
    query = """
    SELECT p.name, p.register_number, r.score, r.total_questions, r.time_taken, r.cheating_warnings
    FROM participants p
    LEFT JOIN results r ON p.id = r.participant_id
    WHERE p.quiz_id = ?
    """
    rows = db.execute(query, (quiz_id,)).fetchall()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Register Number', 'Score', 'Total Questions', 'Time Taken', 'Cheating Warnings'])
    
    for row in rows:
        writer.writerow([row['name'], row['register_number'], row['score'], row['total_questions'], row['time_taken'], row['cheating_warnings']])
    
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=quiz_{quiz_id}_results.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@app.route('/api/cheating_log', methods=['POST'])
def log_cheating():
    data = request.json
    p_id = session.get('participant_id')
    if p_id:
        db = get_db()
        db.execute("INSERT INTO cheating_logs (participant_id, event_type) VALUES (?, ?)",
                   (p_id, data['event_type']))
        db.commit()
    return jsonify({'success': True})

@app.route('/admin/delete_quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    # Delete associated results and participants first if needed (though SQLite triggers or cascade would be better)
    db.execute("DELETE FROM results WHERE participant_id IN (SELECT id FROM participants WHERE quiz_id = ?)", (quiz_id,))
    db.execute("DELETE FROM participants WHERE quiz_id = ?", (quiz_id,))
    db.execute("DELETE FROM questions WHERE quiz_id = ?", (quiz_id,))
    db.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
    db.commit()
    return redirect(url_for('admin_dashboard'))

@app.before_request
def setup_db():
    if not hasattr(app, 'db_initialized'):
        try:
            init_db()
            app.db_initialized = True
        except Exception as e:
            print(f"Failed to initialize DB: {e}")

if __name__ == '__main__':
    app.run(debug=True)
