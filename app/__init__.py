from datetime import datetime
from flask import Flask, render_template
from app.config import Config
from app.extensions import init_db, db
from app.services.pdf_service import PdfService

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Database & Data Seeding
    init_db(app)

    # Ensure uploads folder and sample PDFs exist
    PdfService.ensure_sample_pdfs_exist(app.static_folder)

    # Register Blueprints
    from app.routes.home import home_bp
    from app.routes.subjects import subjects_bp
    from app.routes.exams import exams_bp
    from app.routes.papers import papers_bp
    from app.routes.tests import tests_bp
    from app.routes.results import results_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(exams_bp)
    app.register_blueprint(papers_bp)
    app.register_blueprint(tests_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Global Template Context Processor
    @app.context_processor
    def inject_global_data():
        active_exams = []
        if db:
            active_exams = db.exams.find({'active': True})
        return {
            'nav_exams': active_exams,
            'current_year': datetime.utcnow().year,
            'app_name': 'ParikshaSetu',
            'app_name_mr': 'परीक्षामार्ग'
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app
