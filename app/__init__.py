import os
from flask import Flask
from app.config import config_by_name
from app.extensions import db, migrate, jwt, limiter, cors


def create_app(config_name: str = None) -> Flask:
    """Application factory pattern."""
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)

    with app.app_context():
        db.create_all()
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    return app


def register_extensions(app: Flask):
    """Initialize Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    cors.init_app(app)


def register_blueprints(app: Flask):
    """Register Flask blueprints."""
    from app.routes.auth import auth_bp
    from app.routes.resume import resume_bp
    from app.routes.job import job_bp
    from app.routes.match import match_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.pages import pages_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(resume_bp, url_prefix="/api/resumes")
    app.register_blueprint(job_bp, url_prefix="/api/jobs")
    app.register_blueprint(match_bp, url_prefix="/api/matches")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(pages_bp)


def register_error_handlers(app: Flask):
    """Register error handlers."""

    @app.errorhandler(400)
    def bad_request(error):
        return {"error": "Bad request", "code": "BAD_REQUEST"}, 400

    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Resource not found", "code": "NOT_FOUND"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {"error": "Internal server error", "code": "INTERNAL_ERROR"}, 500


app = create_app()
