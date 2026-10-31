from flask import Blueprint, render_template, abort
from app.extensions import db

subjects_bp = Blueprint('subjects', __name__)

@subjects_bp.route('/police-bharti')
def police_bharti():
    """First Main Tab: Maharashtra Police Bharti Subject Command Center"""
    exam = db.exams.find_one({'id': 'police-bharti'})
    subjects = db.subjects.find({'exam_id': 'police-bharti'})
    papers = db.papers.find({'exam_id': 'police-bharti'}, sort=[('year', -1)])
    
    # Calculate questions count per subject
    for s in subjects:
        s['question_count'] = db.questions.count_documents({'subject_id': s.get('id')})

    return render_template(
        'police_bharti.html',
        exam=exam,
        subjects=subjects,
        papers=papers
    )

@subjects_bp.route('/subjects/<subject_id>')
def subject_detail(subject_id):
    """Subject detail page with topic breakdown and interactive sample questions"""
    subject = db.subjects.find_one({'id': subject_id})
    if not subject:
        abort(404)

    exam = db.exams.find_one({'id': subject.get('exam_id')})
    questions = db.questions.find({'subject_id': subject_id})
    related_papers = db.papers.find({'exam_id': subject.get('exam_id')}, sort=[('year', -1)])

    return render_template(
        'subjects.html',
        subject=subject,
        exam=exam,
        questions=questions,
        related_papers=related_papers
    )
