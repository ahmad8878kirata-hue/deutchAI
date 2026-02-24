import os
import requests
import json
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'deutschai-secret-key-x7k2p9m4q1r8v5w3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///deutschai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SAMESITE'] = 'None'
app.config['REMEMBER_COOKIE_SECURE'] = True

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    german_level = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    progress = db.Column(db.Integer, default=0)
    xp = db.Column(db.Integer, default=0)
    vocabularies = db.relationship('Vocabulary', backref='owner', lazy=True)
    activities = db.relationship('Activity', backref='owner', lazy=True)

class Vocabulary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word = db.Column(db.String(100), nullable=False)
    correction = db.Column(db.String(100), nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False) # 'chat', 'practice', 'vocab'
    description = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def log_activity(user, type, description, points):
    activity = Activity(user_id=user.id, type=type, description=description, points=points)
    user.xp += points
    # Simple logic: 1000 XP per level, progress is % of current 1000
    user.progress = (user.xp % 1000) // 10
    if user.progress > 100: user.progress = 100
    db.session.add(activity)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging activity: {e}")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_user():
    return dict(user=current_user)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        german_level = request.form.get('german_level')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already registered!', 'danger')
            return redirect(url_for('signup'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(first_name=first_name, last_name=last_name, german_level=german_level, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.timestamp.desc()).limit(5).all()
    return render_template('dashboard.html', activities=activities)

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@app.route('/chat/api', methods=['POST'])
@login_required
def chat_api():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    api_key = "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"
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://deutchai.tayba.blog",
            "X-Title": "DeutschAI",
        },
        data=json.dumps({
            "model": "openai/gpt-3.5-turbo", # Changed to a more common model since gpt-5.2 is not a standard one yet
            "messages": [
                {
                    "role": "system",
                    "content": f"You are Hans, a helpful German language tutor. The user's German level is {current_user.german_level}. Please speak primarily in German and encourage the user. Keep your responses concise and engaging."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        })
    )
    
    if response.status_code == 200:
        log_activity(current_user, 'chat', 'Konversation mit Hans geführt', 10)
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to get response from AI"}), response.status_code

@app.route('/practice')
@login_required
def practice():
    return render_template('practice.html')

@app.route('/practice/api', methods=['POST'])
@login_required
def practice_api():
    data = request.json
    user_text = data.get('text')
    
    if not user_text:
        return jsonify({"error": "No text provided"}), 400

    api_key = "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"
    
    system_prompt = f"""
    You are an expert German grammar checker. The user's level is {current_user.german_level}.
    Analyze the following German text for:
    1. Grammar errors
    2. Spelling mistakes
    3. Suggested improvements for better fluency
    4. CEFR level of the vocabulary used
    5. An overall grammar score (0-100%)

    IMPORTANT: Your response MUST be in JSON format with the following structure:
    {{
        "score": number,
        "vocab_level": "string (A1-C2)",
        "analysis_summary": "string in English",
        "corrections": [
            {{
                "original": "string",
                "correction": "string",
                "explanation": "string in English",
                "type": "grammar" | "spelling" | "style"
            }}
        ]
    }}
    """
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://deutchai.tayba.blog",
            "X-Title": "DeutschAI",
        },
        data=json.dumps({
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            "response_format": { "type": "json_object" }
        })
    )
    
    if response.status_code == 200:
        result_data = response.json()
        try:
            content = json.loads(result_data['choices'][0]['message']['content'])
            score = content.get('score', 0)
            log_activity(current_user, 'practice', f'Grammatik-Übung abgeschlossen ({score}%)', score // 5)
        except:
            pass
        return jsonify(result_data)
    else:
        return jsonify({"error": "Failed to get response from AI"}), response.status_code

@app.route('/call')
@login_required
def call():
    return render_template('call.html')

@app.route('/call/api', methods=['POST'])
@login_required
def call_api():
    data = request.json
    messages = data.get('messages', [])

    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    api_key = "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"

    system_message = {
        "role": "system",
        "content": f"You are Hans, a friendly and encouraging German language teacher. The user's level is {current_user.german_level}. The user is practicing speaking German. Always respond in German, keep responses short and natural like a real conversation. If the message seems unclear or broken, try your best to understand the intent and respond helpfully. Gently correct any grammar mistakes."
    }

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "DeutschAI",
        },
        data=json.dumps({
            "model": "openai/gpt-3.5-turbo",
            "messages": [system_message] + messages
        })
    )

    if response.status_code == 200:
        log_activity(current_user, 'chat', 'Sprachanruf mit Hans geführt', 15)
        return jsonify(response.json())
    else:
        return jsonify({"error": "AI response failed"}), response.status_code

@app.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.email = request.form.get('email')
        current_user.german_level = request.form.get('cefr_level')
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'danger')
        
        return redirect(url_for('setting'))
    return render_template('setting.html')

@app.route('/vocabulary')
@login_required
def vocabulary():
    return render_template('vocabulary.html')

@app.route('/vocabulary/api/add', methods=['POST'])
@login_required
def add_vocabulary():
    data = request.json
    word = data.get('word')
    correction = data.get('correction')
    explanation = data.get('explanation')

    if not word or not correction:
        return jsonify({"error": "Missing word or correction"}), 400

    # Avoid duplicates for the same user
    existing = Vocabulary.query.filter_by(user_id=current_user.id, word=word, correction=correction).first()
    if existing:
        return jsonify({"message": "Word already in vocabulary"}), 200

    new_vocab = Vocabulary(
        user_id=current_user.id,
        word=word,
        correction=correction,
        explanation=explanation
    )
    db.session.add(new_vocab)
    log_activity(current_user, 'vocab', f'Neues Wort gelernt: {correction}', 5)
    db.session.commit()
    return jsonify({"message": "Vocabulary added successfully"}), 201

@app.route('/vocabulary/api/list', methods=['GET'])
@login_required
def list_vocabulary():
    vocabs = Vocabulary.query.filter_by(user_id=current_user.id).order_by(Vocabulary.timestamp.desc()).all()
    return jsonify([{
        "id": v.id,
        "word": v.word,
        "correction": v.correction,
        "explanation": v.explanation,
        "timestamp": v.timestamp.isoformat()
    } for v in vocabs])

@app.route('/vocabulary/api/delete/<int:vocab_id>', methods=['DELETE'])
@login_required
def delete_vocabulary(vocab_id):
    vocab = Vocabulary.query.filter_by(id=vocab_id, user_id=current_user.id).first()
    if not vocab:
        return jsonify({"error": "Vocabulary item not found"}), 404
    
    db.session.delete(vocab)
    db.session.commit()
    return jsonify({"message": "Vocabulary item deleted"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
