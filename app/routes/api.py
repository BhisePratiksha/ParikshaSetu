from flask import Blueprint, jsonify, request, session, current_app
from app.extensions import db
from app.services.paper_service import PaperService
from app.services.api_import_service import ApiImportService

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/status')
def api_status():
    return jsonify({
        'status': 'success',
        'application': 'ParikshaSetu Government Exam Preparation Platform',
        'version': '1.0.0',
        'database': 'MongoDB / MongoCompatibleStore',
        'total_exams': db.exams.count_documents(),
        'total_papers': db.papers.count_documents(),
        'total_questions': db.questions.count_documents()
    })

@api_bp.route('/papers', methods=['GET'])
def get_papers():
    """GET /api/papers and GET /api/papers?exam_id=police-bharti&year=2025"""
    exam_id = request.args.get('exam_id')
    year = request.args.get('year')
    district = request.args.get('district')
    exam_type = request.args.get('exam_type')
    search = request.args.get('search')

    papers = PaperService.get_papers(
        exam_id=exam_id,
        year=year,
        district=district,
        exam_type=exam_type,
        search=search
    )

    return jsonify({
        'status': 'success',
        'total_papers': len(papers),
        'papers': papers
    })

@api_bp.route('/papers/<paper_id>', methods=['GET'])
def get_paper(paper_id):
    """GET /api/papers/<paper_id>"""
    paper = PaperService.get_paper_by_id(paper_id)
    if not paper:
        return jsonify({'status': 'error', 'message': 'Paper not found'}), 404

    # Attach exam details
    exam = db.exams.find_one({'id': paper.get('exam_id')})
    return jsonify({
        'status': 'success',
        'paper': paper,
        'exam': exam
    })

@api_bp.route('/exams', methods=['GET'])
def get_exams():
    exams = db.exams.find({'active': True})
    return jsonify({
        'status': 'success',
        'total_exams': len(exams),
        'exams': exams
    })

@api_bp.route('/admin/papers/import', methods=['POST'])
def import_papers_api():
    """POST /api/admin/papers/import - Protected admin import endpoint"""
    # Check session auth or API token header
    user_role = session.get('user_role')
    auth_header = request.headers.get('Authorization', '')

    is_authorized = (user_role == 'admin') or (auth_header == f"Bearer {current_app.config['SECRET_KEY']}")
    if not is_authorized:
        return jsonify({'status': 'error', 'message': 'Unauthorized: Admin role or Bearer token required'}), 401

    payload = request.get_json(silent=True) or {}
    source_type = payload.get('source_type', 'local')

    if source_type == 'local':
        local_path = current_app.config.get('LOCAL_PAPERS_PATH')
        res = ApiImportService.import_from_local_file(local_path)
    else:
        url = payload.get('url') or current_app.config.get('PAPERS_API_URL')
        res = ApiImportService.import_from_external_url(url)

    status_code = 200 if res.get('success') else 400
    return jsonify(res), status_code
