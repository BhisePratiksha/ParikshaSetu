from flask import Blueprint, render_template, abort
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
