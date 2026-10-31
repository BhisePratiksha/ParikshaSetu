from functools import wraps
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('कृपया पुढे जाण्यापूर्वी लॉगिन करा (Please login to continue).', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('कृपया प्रशासक (Admin) म्हणून लॉगिन करा.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('user_role') != 'admin':
            flash('या पृष्ठासाठी प्रशासकीय अधिकार (Admin Access) आवश्यक आहेत.', 'danger')
            return redirect(url_for('home.index'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        next_url = request.form.get('next') or request.args.get('next')

        if not email or not password:
            flash('ईमेल आणि पासवर्ड भरणे आवश्यक आहे.', 'danger')
            return render_template('auth/login.html')

        user = db.users.find_one({'email': email})
        if user and check_password_hash(user.get('password_hash', ''), password):
            session.clear()
            session['user_id'] = user.get('_id') or user.get('id')
            session['user_name'] = user.get('name')
            session['user_email'] = user.get('email')
            session['user_role'] = user.get('role', 'student')

            flash(f'स्वागत आहे, {user.get("name")}! लॉगिन यशस्वी झाले.', 'success')
            
            if user.get('role') == 'admin':
                return redirect(next_url or url_for('admin.dashboard'))
            return redirect(next_url or url_for('results.my_results'))

        flash('अवैध ईमेल किंवा पासवर्ड. कृपया पुन्हा तपासा.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        target_exam = request.form.get('target_exam', 'police-bharti')

        if not name or not email or not password:
            flash('कृपया सर्व आवश्यक माहिती भरा.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('पासवर्ड किमान ६ अक्षरांचा असावा.', 'warning')
            return render_template('auth/register.html')

        existing = db.users.find_one({'email': email})
        if existing:
            flash('हा ईमेल आधीच नोंदणीकृत आहे. कृपया लॉगिन करा.', 'warning')
            return redirect(url_for('auth.login'))

        new_user = {
            'name': name,
            'email': email,
            'password_hash': generate_password_hash(password),
            'role': 'student',
            'target_exam': target_exam,
            'is_active': True,
            'created_at': datetime.utcnow().isoformat()
        }
        res = db.users.insert_one(new_user)
        user_id = getattr(res, 'inserted_id', new_user.get('_id'))

        session.clear()
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email
        session['user_role'] = 'student'

        flash('नोंदणी यशस्वी झाली! आपले ParikshaSetu वर स्वागत आहे.', 'success')
        return redirect(url_for('subjects.police_bharti'))

    exams = db.exams.find({'active': True})
    return render_template('auth/register.html', exams=exams)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('आपण यशस्वीरित्या लॉगआउट झाला आहात.', 'info')
    return redirect(url_for('home.index'))
