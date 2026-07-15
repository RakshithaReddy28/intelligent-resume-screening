from app.routes.auth import auth_bp
from app.routes.resume import resume_bp
from app.routes.job import job_bp
from app.routes.match import match_bp
from app.routes.dashboard import dashboard_bp

__all__ = [
    "auth_bp",
    "resume_bp",
    "job_bp",
    "match_bp",
    "dashboard_bp",
]
