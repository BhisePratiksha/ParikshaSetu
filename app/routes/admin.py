import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from app.extensions import db
from app.routes.auth import admin_required
from app.services.api_import_service import ApiImportService
from app.services.pdf_service import PdfService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin command center overview with core metrics"""
    stats = {
        'exams': db.exams.count_documents(),
        'subjects': db.subjects.count_documents(),
        'papers': db.papers.count_documents(),
        'questions': db.questions.count_documents(),
        'users': db.users.count_documents(),
        'results': db.results.count_documents()
    }
    recent_papers = db.papers.find(sort=[('year', -1)])[:5]
    recent_results = db.results.find(sort=[('submitted_at', -1)])[:5]
    import_logs = db.api_import_logs.find(sort=[('timestamp', -1)])[:5]

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_papers=recent_papers,
        recent_results=recent_results,
        import_logs=import_logs
    )

# --- EXAM MANAGEMENT ---
@admin_bp.route('/exams', methods=['GET', 'POST'])
@admin_required
def manage_exams():
    if request.method == 'POST':
        exam_id = request.form.get('id', '').strip().lower().replace(' ', '-')
        name = request.form.get('name', '').strip()
        name_mr = request.form.get('name_mr', '').strip()
        category = request.form.get('category', '').strip()
        duration = int(request.form.get('duration_minutes', 90))
        questions = int(request.form.get('total_questions', 100))
        marks = float(request.form.get('total_marks', 100))
        negative = float(request.form.get('negative_marks', 0.0))

        if not exam_id or not name:
            flash('परीक्षेचे नाव व ओळख क्रमांक आवश्यक आहे.', 'danger')
            return redirect(url_for('admin.manage_exams'))

        doc = {
            'id': exam_id,
            'name': name,
            'name_mr': name_mr or name,
            'category': category or 'State Exam',
            'duration_minutes': duration,
            'total_questions': questions,
            'total_marks': marks,
            'negative_marks': negative,
            'active': True
        }
        db.exams.update_one({'id': exam_id}, {'$set': doc}, upsert=True)
        flash(f'परीक्षा यशस्वीरित्या जोडली/अद्ययावत केली: {name}', 'success')
        return redirect(url_for('admin.manage_exams'))

    exams = db.exams.find()
    return render_template('admin/exams.html', exams=exams)

@admin_bp.route('/exams/delete/<exam_id>', methods=['POST'])
@admin_required
def delete_exam(exam_id):
    db.exams.delete_one({'id': exam_id})
    flash('परीक्षा हटवली.', 'info')
    return redirect(url_for('admin.manage_exams'))

# --- SUBJECT MANAGEMENT ---
@admin_bp.route('/subjects', methods=['GET', 'POST'])
@admin_required
def manage_subjects():
    if request.method == 'POST':
        subj_id = request.form.get('id', '').strip().lower().replace(' ', '-')
        exam_id = request.form.get('exam_id')
        name = request.form.get('name', '').strip()
        name_mr = request.form.get('name_mr', '').strip()
        topics_str = request.form.get('topics', '')
        topics = [t.strip() for t in topics_str.split('\n') if t.strip()]

        if not subj_id or not name or not exam_id:
            flash('सर्व आवश्यक फील्ड भरा.', 'danger')
            return redirect(url_for('admin.manage_subjects'))

        doc = {
            'id': subj_id,
            'exam_id': exam_id,
            'name': name,
            'name_mr': name_mr or name,
            'topics': topics,
            'icon': request.form.get('icon', 'bi-book'),
            'color': request.form.get('color', '#6366F1'),
            'weightage_percent': int(request.form.get('weightage', 20))
        }
        db.subjects.update_one({'id': subj_id}, {'$set': doc}, upsert=True)
        flash(f'विषय जतन करण्यात आला: {name}', 'success')
        return redirect(url_for('admin.manage_subjects'))

    subjects = db.subjects.find()
    exams = db.exams.find({'active': True})
    return render_template('admin/subjects.html', subjects=subjects, exams=exams)

# --- QUESTION PAPER MANAGEMENT ---
@admin_bp.route('/papers', methods=['GET', 'POST'])
@admin_required
def manage_papers():
    if request.method == 'POST':
        paper_id = request.form.get('id', '').strip() or f"paper_{uuid.uuid4().hex[:6]}"
        exam_id = request.form.get('exam_id')
        year = int(request.form.get('year', 2025))
        district = request.form.get('district', 'Maharashtra')
        exam_type = request.form.get('exam_type', 'Recruitment')
        title = request.form.get('title', '').strip()
        duration = int(request.form.get('duration_minutes', 90))
        total_q = int(request.form.get('total_questions', 100))
        total_m = float(request.form.get('total_marks', 100))
        neg_m = float(request.form.get('negative_marks', 0.0))

        pdf_url = request.form.get('pdf_url', '').strip() or None
        answer_key_url = request.form.get('answer_key_url', '').strip() or None

        # Check for uploaded files
        if 'pdf_file' in request.files and request.files['pdf_file'].filename:
            res = PdfService.save_pdf(request.files['pdf_file'], current_app.config['UPLOAD_FOLDER'], prefix=f"{exam_id}_{year}")
            if res.get('success'):
                pdf_url = res.get('file_url')
            else:
                flash(f"PDF अपलोड त्रुटी: {res.get('message')}", 'danger')

        if 'answer_key_file' in request.files and request.files['answer_key_file'].filename:
            res = PdfService.save_pdf(request.files['answer_key_file'], current_app.config['UPLOAD_FOLDER'], prefix=f"key_{exam_id}_{year}")
            if res.get('success'):
                answer_key_url = res.get('file_url')

        doc = {
            'id': paper_id,
            'exam_id': exam_id,
            'year': year,
            'district': district,
            'exam_type': exam_type,
            'title': title,
            'pdf_url': pdf_url,
            'answer_key_url': answer_key_url,
            'duration_minutes': duration,
            'total_questions': total_q,
            'total_marks': total_m,
            'negative_marks': neg_m,
            'shift': request.form.get('shift', 'Morning Shift')
        }
        db.papers.update_one({'id': paper_id}, {'$set': doc}, upsert=True)
        flash(f'प्रश्नपत्रिका जोडली: {title}', 'success')
        return redirect(url_for('admin.manage_papers'))

    papers = db.papers.find(sort=[('year', -1)])
    exams = db.exams.find({'active': True})
    return render_template('admin/papers.html', papers=papers, exams=exams)

@admin_bp.route('/papers/delete/<paper_id>', methods=['POST'])
@admin_required
def delete_paper(paper_id):
    db.papers.delete_one({'id': paper_id})
    flash('प्रश्नपत्रिका हटवली.', 'info')
    return redirect(url_for('admin.manage_papers'))

# --- QUESTION BANK MANAGEMENT ---
@admin_bp.route('/questions', methods=['GET', 'POST'])
@admin_required
def manage_questions():
    if request.method == 'POST':
        q_id = request.form.get('id', '').strip() or f"q_{uuid.uuid4().hex[:6]}"
        exam_id = request.form.get('exam_id')
        subject_id = request.form.get('subject_id')
        paper_id = request.form.get('paper_id')
        
        opt_a = request.form.get('option_a', '').strip()
        opt_b = request.form.get('option_b', '').strip()
        opt_c = request.form.get('option_c', '').strip()
        opt_d = request.form.get('option_d', '').strip()
        correct_idx = int(request.form.get('correct_index', 0))
        options = [opt_a, opt_b, opt_c, opt_d]

        doc = {
            'id': q_id,
            'exam_id': exam_id,
            'subject_id': subject_id,
            'paper_id': paper_id,
            'question_text': request.form.get('question_text', '').strip(),
            'question_text_en': request.form.get('question_text_en', '').strip(),
            'topic': request.form.get('topic', 'General'),
            'options': options,
            'correct_index': correct_idx,
            'correct_answer': options[correct_idx],
            'explanation': request.form.get('explanation', '').strip(),
            'marks': float(request.form.get('marks', 1.0)),
            'negative_marks': float(request.form.get('negative_marks', 0.0))
        }
        db.questions.update_one({'id': q_id}, {'$set': doc}, upsert=True)
        flash('प्रश्न यशस्वीरित्या प्रश्नसंचात जोडला.', 'success')
        return redirect(url_for('admin.manage_questions'))

    questions = db.questions.find(sort=[('_id', -1)])[:50]
    exams = db.exams.find({'active': True})
    subjects = db.subjects.find()
    papers = db.papers.find()
    return render_template(
        'admin/questions.html',
        questions=questions,
        exams=exams,
        subjects=subjects,
        papers=papers
    )

# --- MOCK API IMPORT TOOL ---
@admin_bp.route('/import', methods=['GET', 'POST'])
@admin_required
def import_papers():
    """Mock API Integration Tool: read from local JSON or external URL"""
    if request.method == 'POST':
        source_type = request.form.get('source_type', 'local')
        if source_type == 'local':
            local_path = current_app.config.get('LOCAL_PAPERS_PATH')
            res = ApiImportService.import_from_local_file(local_path)
        else:
            api_url = request.form.get('api_url', '').strip() or current_app.config.get('PAPERS_API_URL')
            res = ApiImportService.import_from_external_url(api_url)

        if res.get('success'):
            flash(f"यशस्वी आयात: {res.get('message')}", 'success')
        else:
            flash(f"आयात अयशस्वी: {res.get('message')}", 'danger')

        return redirect(url_for('admin.import_papers'))

    logs = db.api_import_logs.find(sort=[('timestamp', -1)])[:10]
    default_url = current_app.config.get('PAPERS_API_URL')
    return render_template('admin/import_papers.html', logs=logs, default_url=default_url)
