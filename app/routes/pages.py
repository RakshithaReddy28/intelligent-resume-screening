from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    return render_template("dashboard/index.html")


@pages_bp.route("/login")
def login():
    return render_template("auth/login.html")


@pages_bp.route("/register")
def register():
    return render_template("auth/register.html")


@pages_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard/index.html")


@pages_bp.route("/resumes")
def resumes():
    return render_template("resumes/upload.html")


@pages_bp.route("/jobs")
def jobs():
    return render_template("jobs/list.html")


@pages_bp.route("/jobs/<int:job_id>")
def job_detail(job_id):
    return render_template("jobs/detail.html", job_id=job_id)
