from flask import Blueprint, render_template, abort, session, redirect, url_for
from app.extensions import db

results_bp = Blueprint('results', __name__)

@results_bp.route('/results/<result_id>')
def result_view(result_id):
    """Detailed score card, accuracy metrics, subject breakdown and answer key review with explanations"""
    result = db.results.find_one({'id': result_id})
    if not result:
        abort(404)

    paper = db.papers.find_one({'id': result.get('paper_id')})
    exam = db.exams.find_one({'id': result.get('exam_id')})

    return render_template(
        'results.html',
        result=result,
        paper=paper,
        exam=exam
    )

@results_bp.route('/my-results')
def my_results():
    """Student personal analytics dashboard: test history, score trends, weak subjects, study suggestions"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login', next='/my-results'))

    user = db.users.find_one({'_id': user_id}) or db.users.find_one({'id': user_id})
    
    # Fetch student's test history
    history = db.results.find({'user_id': user_id}, sort=[('submitted_at', -1)])
    
    # Aggregate student analytics
    total_tests = len(history)
    avg_score = round(sum(r.get('percentage', 0) for r in history) / total_tests, 1) if total_tests > 0 else 0
    highest_score = max([r.get('percentage', 0) for r in history], default=0)

    # Aggregate weak subject trends across attempts
    weak_subject_counts = {}
    for h in history:
        for subj, d in h.get('subject_breakdown', {}).items():
            if d.get('percentage', 0) < 60:
                weak_subject_counts[subj] = weak_subject_counts.get(subj, 0) + 1

    sorted_weak = sorted(weak_subject_counts.items(), key=lambda x: x[1], reverse=True)

    return render_template(
        'dashboard.html',
        user=user,
        history=history,
        total_tests=total_tests,
        avg_score=avg_score,
        highest_score=highest_score,
        weak_subjects=[w[0] for w in sorted_weak[:3]]
    )
