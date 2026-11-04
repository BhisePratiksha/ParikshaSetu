import os
from flask import Blueprint, render_template, request, abort, send_file, current_app, flash, redirect, url_for
from app.extensions import db
from app.services.paper_service import PaperService

papers_bp = Blueprint('papers', __name__)

@papers_bp.route('/previous-year-papers')
@papers_bp.route('/papers')
def papers_list():
    """Hierarchy: Exam -> Year -> District -> Paper with multi-criteria filters"""
    exam_id = request.args.get('exam_id', 'all')
    year = request.args.get('year', 'all')
    district = request.args.get('district', 'all')
    exam_type = request.args.get('exam_type', 'all')
    search = request.args.get('search', '').strip()

    papers = PaperService.get_papers(
        exam_id=exam_id,
        year=year,
        district=district,
        exam_type=exam_type,
        search=search
    )

    # Attach exam details to paper for card rendering
    exams_map = {e['id']: e for e in db.exams.find()}
    for p in papers:
        p['exam'] = exams_map.get(p.get('exam_id'), {})

    # Filter dropdown lists
    exams = db.exams.find({'active': True})
    years = PaperService.get_distinct_years(exam_id=exam_id if exam_id != 'all' else None)
    districts = PaperService.get_distinct_districts(exam_id=exam_id if exam_id != 'all' else None)

    return render_template(
        'papers.html',
        papers=papers,
        exams=exams,
        years=years,
        districts=districts,
        selected_exam=exam_id,
        selected_year=year,
        selected_district=district,
        selected_type=exam_type,
        search_query=search
    )

@papers_bp.route('/papers/<paper_id>')
def paper_detail(paper_id):
    """Paper details page with View PDF, Download, Answer Key, and Solve Online options"""
    paper = PaperService.get_paper_by_id(paper_id)
    if not paper:
        abort(404)

    exam = db.exams.find_one({'id': paper.get('exam_id')})
    question_count = db.questions.count_documents({'paper_id': paper_id})
    if question_count == 0 and exam:
        question_count = db.questions.count_documents({'exam_id': exam.get('id')})

    return render_template(
        'paper_details.html',
        paper=paper,
        exam=exam,
        question_count=question_count
    )

@papers_bp.route('/papers/<paper_id>/solutions')
def view_solutions(paper_id):
    """View all extracted questions, options, verified answers, and detailed pedagogical explanations"""
    paper = PaperService.get_paper_by_id(paper_id)
    if not paper:
        abort(404)

    exam = db.exams.find_one({'id': paper.get('exam_id')})
    subject_filter = request.args.get('subject', 'all')
    search = request.args.get('search', '').strip()

    query = {'paper_id': paper_id}
    if subject_filter != 'all':
        query['subject_id'] = subject_filter

    questions = db.questions.find(query, sort=[('question_number', 1)])
    
    # If no paper-specific questions exist, fallback to general exam questions
    if not questions and exam:
        query_exam = {'exam_id': exam.get('id')}
        if subject_filter != 'all':
            query_exam['subject_id'] = subject_filter
        questions = db.questions.find(query_exam)

    if search:
        questions = [q for q in questions if search.lower() in q.get('question_text', '').lower() or search.lower() in q.get('explanation', '').lower()]

    subjects = db.subjects.find({'exam_id': paper.get('exam_id')})

    return render_template(
        'paper_solutions.html',
        paper=paper,
        exam=exam,
        questions=questions,
        subjects=subjects,
        selected_subject=subject_filter,
        search_query=search
    )

@papers_bp.route('/papers/<paper_id>/pdf')
def view_pdf(paper_id):
    """Dedicated in-browser embedded PDF viewer with graceful fallback"""
    paper = PaperService.get_paper_by_id(paper_id)
    if not paper:
        abort(404)

    pdf_type = request.args.get('type', 'question_paper') # 'question_paper' or 'answer_key'
    target_url = paper.get('answer_key_url') if pdf_type == 'answer_key' else paper.get('pdf_url')

    exam = db.exams.find_one({'id': paper.get('exam_id')})

    return render_template(
        'pdf_viewer.html',
        paper=paper,
        exam=exam,
        pdf_url=target_url,
        pdf_type=pdf_type
    )

@papers_bp.route('/papers/<paper_id>/download')
def download_pdf(paper_id):
    """Secure direct download endpoint for question paper or answer key"""
    paper = PaperService.get_paper_by_id(paper_id)
    if not paper:
        abort(404)

    pdf_type = request.args.get('type', 'question_paper')
    target_url = paper.get('answer_key_url') if pdf_type == 'answer_key' else paper.get('pdf_url')

    if not target_url:
        flash('या प्रश्नपत्रिकेची PDF फाईल सध्या उपलब्ध नाही.', 'warning')
        return redirect(url_for('papers.paper_detail', paper_id=paper_id))

    # If it is a local static upload
    if target_url.startswith('/static/'):
        rel = target_url.replace('/static/', '')
        abs_path = os.path.join(current_app.root_path, 'static', rel)
        if os.path.exists(abs_path):
            filename = os.path.basename(abs_path)
            return send_file(abs_path, as_attachment=True, download_name=f"{paper.get('id')}_{filename}")

    # Fallback redirect to external URL
    return redirect(target_url)
