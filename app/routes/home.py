from flask import Blueprint, render_template
from app.extensions import db

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    exams = db.exams.find({'active': True})
    papers = db.papers.find(sort=[('year', -1)])
    recent_papers = papers[:6]
    
    # Platform stats
    stats = {
        'total_exams': db.exams.count_documents(),
        'total_papers': len(papers),
        'total_questions': db.questions.count_documents(),
        'total_users': db.users.count_documents()
    }
    
    # Police Bharti subjects for home preview
    police_subjects = db.subjects.find({'exam_id': 'police-bharti'})
    
    return render_template(
        'home.html',
        exams=exams,
        recent_papers=recent_papers,
        stats=stats,
        police_subjects=police_subjects
    )
