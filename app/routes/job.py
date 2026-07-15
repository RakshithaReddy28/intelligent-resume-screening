from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.job import Job, JobSkill
from app.models.skill import Skill
from app.models.enums import JobStatus, UserRole
from app.models.user import User

job_bp = Blueprint("job", __name__)


@job_bp.route("/browse", methods=["GET"])
@jwt_required()
def browse_jobs():
    """Browse all active jobs (candidate view)."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    search = request.args.get("search", "").strip()

    query = Job.query.filter_by(status=JobStatus.ACTIVE)

    if search:
        query = query.filter(
            db.or_(
                Job.title.ilike(f"%{search}%"),
                Job.company.ilike(f"%{search}%"),
                Job.description.ilike(f"%{search}%"),
                Job.location.ilike(f"%{search}%"),
            )
        )

    pagination = query.order_by(Job.created_at.desc()).paginate(
        page=page, per_page=per_page
    )

    jobs = []
    for j in pagination.items:
        skills = []
        for js in j.skills:
            skills.append({
                "name": js.skill.canonical_name,
                "is_required": js.is_required,
            })
        jobs.append({
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "description": j.description[:200] + "..." if len(j.description or "") > 200 else j.description,
            "location": j.location,
            "job_type": j.job_type,
            "experience_range": f"{j.experience_min_years or 0}-{j.experience_max_years or '?'} years",
            "education_level": j.education_level,
            "skills": skills,
            "created_at": j.created_at.isoformat() if j.created_at else None,
        })

    return jsonify({
        "jobs": jobs,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page,
    }), 200


@job_bp.route("/<int:job_id>/detail", methods=["GET"])
@jwt_required()
def get_job_detail(job_id):
    """Get detailed job info for candidates."""
    job = Job.query.filter_by(id=job_id, status=JobStatus.ACTIVE).first()
    if not job:
        return jsonify({"error": "Job not found"}), 404

    skills = []
    for js in job.skills:
        skills.append({
            "name": js.skill.canonical_name,
            "is_required": js.is_required,
        })

    return jsonify({
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "location": job.location,
        "job_type": job.job_type,
        "experience_min_years": job.experience_min_years,
        "experience_max_years": job.experience_max_years,
        "education_level": job.education_level,
        "skills": skills,
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }), 200


@job_bp.route("", methods=["POST"])
@jwt_required()
def create_job():
    """Create a new job posting."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != UserRole.RECRUITER:
        return jsonify({"error": "Only recruiters can create jobs"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ["title", "company", "description"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    job = Job(
        recruiter_id=user_id,
        title=data["title"],
        company=data["company"],
        description=data["description"],
        location=data.get("location"),
        job_type=data.get("job_type", "full-time"),
        experience_min_years=data.get("experience_min_years"),
        experience_max_years=data.get("experience_max_years"),
        education_level=data.get("education_level"),
        status=JobStatus.ACTIVE,
    )
    db.session.add(job)
    db.session.flush()

    skills_data = data.get("skills", [])
    for skill_data in skills_data:
        skill_name = skill_data.get("name", "").strip()
        if not skill_name:
            continue

        skill = Skill.query.filter(
            db.func.lower(Skill.canonical_name) == skill_name.lower()
        ).first()

        if not skill:
            skill = Skill(
                name=skill_name,
                canonical_name=skill_name.lower(),
                category=skill_data.get("category", "general"),
            )
            db.session.add(skill)
            db.session.flush()

        job_skill = JobSkill(
            job_id=job.id,
            skill_id=skill.id,
            is_required=skill_data.get("is_required", True),
        )
        db.session.add(job_skill)

    db.session.commit()

    return jsonify({
        "message": "Job created successfully",
        "job_id": job.id,
    }), 201


@job_bp.route("", methods=["GET"])
@jwt_required()
def list_jobs():
    """List all jobs for the current recruiter."""
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status = request.args.get("status")

    query = Job.query.filter_by(recruiter_id=user_id)

    if status:
        query = query.filter_by(status=JobStatus(status))

    pagination = query.order_by(Job.created_at.desc()).paginate(
        page=page, per_page=per_page
    )

    return jsonify({
        "jobs": [
            {
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "status": j.status.value,
                "created_at": j.created_at.isoformat() if j.created_at else None,
            }
            for j in pagination.items
        ],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page,
    }), 200


@job_bp.route("/<int:job_id>", methods=["GET"])
@jwt_required()
def get_job(job_id):
    """Get detailed information about a job."""
    job = Job.query.get(job_id)

    if not job:
        return jsonify({"error": "Job not found"}), 404

    return jsonify({
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "location": job.location,
        "job_type": job.job_type,
        "experience_min_years": job.experience_min_years,
        "experience_max_years": job.experience_max_years,
        "education_level": job.education_level,
        "status": job.status.value,
        "skills": [
            {
                "name": js.skill.canonical_name,
                "is_required": js.is_required,
            }
            for js in job.skills
        ],
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }), 200


@job_bp.route("/<int:job_id>", methods=["PUT"])
@jwt_required()
def update_job(job_id):
    """Update a job posting."""
    user_id = int(get_jwt_identity())
    job = Job.query.filter_by(id=job_id, recruiter_id=user_id).first()

    if not job:
        return jsonify({"error": "Job not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "title" in data:
        job.title = data["title"]
    if "company" in data:
        job.company = data["company"]
    if "description" in data:
        job.description = data["description"]
    if "location" in data:
        job.location = data["location"]
    if "job_type" in data:
        job.job_type = data["job_type"]
    if "experience_min_years" in data:
        job.experience_min_years = data["experience_min_years"]
    if "experience_max_years" in data:
        job.experience_max_years = data["experience_max_years"]
    if "education_level" in data:
        job.education_level = data["education_level"]
    if "status" in data:
        job.status = JobStatus(data["status"])

    db.session.commit()

    return jsonify({"message": "Job updated successfully"}), 200


@job_bp.route("/<int:job_id>", methods=["DELETE"])
@jwt_required()
def delete_job(job_id):
    """Delete a job posting."""
    user_id = int(get_jwt_identity())
    job = Job.query.filter_by(id=job_id, recruiter_id=user_id).first()

    if not job:
        return jsonify({"error": "Job not found"}), 404

    db.session.delete(job)
    db.session.commit()

    return jsonify({"message": "Job deleted successfully"}), 200
