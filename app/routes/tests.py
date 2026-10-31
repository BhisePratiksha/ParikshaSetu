import json
from flask import Blueprint, render_template, request, redirect, url_for, session, abort, jsonify, flash
from app.extensions import db
from app.services.test_service import TestService
from app.services.scoring_service import ScoringService

tests_bp = Blueprint('tests', __name__)

@tests_bp.route('/mock-tests')
def mock_tests_index():
    """Mock Tests catalog page"""
    exams = db.exams.find({'active': True})
    papers = db.papers.find(sort=[('year', -1)])
    return render_template('mock_tests.html', exams=exams, papers=papers)

@tests_bp.route('/tests/solve/<paper_id>')
def solve_paper(paper_id):
    """Launch interactive CBT exam environment"""
    paper = db.papers.find_one({'id': paper_id})
    if not paper:
        abort(404)

    user_id = session.get('user_id')
    duration = int(paper.get('duration_minutes', 90))

    # Initialize test session
    attempt = TestService.start_attempt(user_id=user_id, paper_id=paper_id, duration_minutes=duration)

    # Fetch SANITIZED questions (answer keys & explanations stripped out for exam security)
    questions = TestService.get_paper_questions(paper_id, sanitize=True)

    if not questions:
        flash('या परीक्षेसाठी प्रश्नसंच अद्याप उपलब्ध नाही. प्रशासक प्रश्न जोडत आहेत.', 'warning')
        return redirect(url_for('papers.paper_detail', paper_id=paper_id))

    exam = db.exams.find_one({'id': paper.get('exam_id')})

    return render_template(
        'solve_paper.html',
        paper=paper,
        exam=exam,
        attempt=attempt,
        questions=questions,
        questions_json=json.dumps(questions, ensure_ascii=False)
    )

@tests_bp.route('/tests/submit/<attempt_id>', methods=['POST'])
def submit_test(attempt_id):
    """Server-side test submission and evaluation"""
    attempt = TestService.get_attempt(attempt_id)
    if not attempt:
        abort(404)

    # If already completed, redirect to existing result
    if attempt.get('status') == 'completed' and attempt.get('result_id'):
        return redirect(url_for('results.result_view', result_id=attempt.get('result_id')))

    user_id = session.get('user_id') or attempt.get('user_id')

    # Parse submitted answers from JSON or form post
    if request.is_json:
        payload = request.get_json() or {}
        submitted_answers = payload.get('answers', {})
        time_taken_seconds = payload.get('time_taken_seconds', 0)
    else:
        # Form post fallback
        submitted_raw = request.form.get('answers_json', '{}')
        try:
            submitted_answers = json.loads(submitted_raw)
        except Exception:
            submitted_answers = {}
        time_taken_seconds = request.form.get('time_taken_seconds', 0)

    # Evaluate on server
    result = ScoringService.evaluate_test(
        attempt_id=attempt_id,
        user_id=user_id,
        submitted_answers=submitted_answers,
        time_taken_seconds=time_taken_seconds
    )

    if request.is_json:
        return jsonify({
            'success': True,
            'result_id': result['id'],
            'redirect_url': url_for('results.result_view', result_id=result['id'])
        })

    return redirect(url_for('results.result_view', result_id=result['id']))
