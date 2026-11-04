from flask import Blueprint, render_template, abort, request
from app.extensions import db
from app.services.paper_service import PaperService

exams_bp = Blueprint('exams', __name__)

@exams_bp.route('/government-exams')
def government_exams():
    """Second Main Tab: Showcase of all other State and Central Government Examinations"""
    # Exclude police-bharti from the 'other exams' listing or show all with badge
    exams = db.exams.find({'active': True})
    
    # Enrich each exam with its isolated database-linked subjects and paper count
    for ex in exams:
        ex['subject_count'] = db.subjects.count_documents({'exam_id': ex['id']})
        ex['paper_count'] = db.papers.count_documents({'exam_id': ex['id']})

    return render_template('government_exams.html', exams=exams)

@exams_bp.route('/exams/<exam_id>')
def exam_details(exam_id):
    """Exam specific page with isolated subjects, year-wise papers, and CBT mock tests"""
    exam = db.exams.find_one({'id': exam_id})
    if not exam:
        abort(404)

    # ONLY fetch subjects associated with this specific exam in database
    subjects = db.subjects.find({'exam_id': exam_id})
    
    # Group papers year-wise
    papers_by_year = PaperService.get_exam_papers_grouped_by_year(exam_id)
    years = sorted(list(papers_by_year.keys()), reverse=True)

    return render_template(
        'exam_details.html',
        exam=exam,
        subjects=subjects,
        papers_by_year=papers_by_year,
        years=years
    )

@exams_bp.route('/exams/<exam_id>/questions')
def exam_questions(exam_id):
    """Category-wise questions view: browse all questions extracted from PDFs for this exam"""
    exam = db.exams.find_one({'id': exam_id})
    if not exam:
        abort(404)

    subject_filter = request.args.get('subject', 'all')
    year_filter = request.args.get('year', 'all')
    paper_filter = request.args.get('paper_id', 'all')
    search = request.args.get('search', '').strip()

    query = {'exam_id': exam_id}
    if subject_filter != 'all':
        query['subject_id'] = subject_filter
    if year_filter != 'all':
        try:
            query['year'] = int(year_filter)
        except ValueError:
            pass
    if paper_filter != 'all':
        query['paper_id'] = paper_filter

    questions = db.questions.find(query, sort=[('question_number', 1)])

    if search:
        s_low = search.lower()
        questions = [q for q in questions if s_low in q.get('question_text', '').lower() or s_low in q.get('explanation', '').lower() or s_low in q.get('topic', '').lower()]

    subjects = db.subjects.find({'exam_id': exam_id})
    papers = db.papers.find({'exam_id': exam_id}, sort=[('year', -1)])
    years = sorted(list({p.get('year') for p in papers if p.get('year')}), reverse=True)

    return render_template(
        'exam_questions.html',
        exam=exam,
        questions=questions,
        subjects=subjects,
        papers=papers,
        years=years,
        selected_subject=subject_filter,
        selected_year=year_filter,
        selected_paper=paper_filter,
        search_query=search
    )
