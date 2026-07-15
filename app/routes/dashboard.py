from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.resume import Resume, ResumeSkill
from app.models.job import Job
from app.models.match import Match
from app.models.skill import Skill
from app.models.enums import UserRole
from app.extensions import db
from sqlalchemy import func

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    """Get dashboard statistics for candidates."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    stats = {}

    # Resume stats
    stats["total_resumes"] = Resume.query.filter_by(user_id=user_id).count()
    stats["parsed_resumes"] = Resume.query.filter_by(user_id=user_id, status="parsed").count()

    # Match stats for this user's resumes
    match_count = (
        db.session.query(Match)
        .join(Resume, Match.resume_id == Resume.id)
        .filter(Resume.user_id == user_id)
        .count()
    )
    stats["total_matches"] = match_count

    # Average match score
    avg_score = (
        db.session.query(func.avg(Match.overall_score))
        .join(Resume, Match.resume_id == Resume.id)
        .filter(Resume.user_id == user_id)
        .scalar()
    )
    stats["average_score"] = round(float(avg_score), 4) if avg_score else 0.0

    # Best match score
    best_score = (
        db.session.query(func.max(Match.overall_score))
        .join(Resume, Match.resume_id == Resume.id)
        .filter(Resume.user_id == user_id)
        .scalar()
    )
    stats["best_score"] = round(float(best_score), 4) if best_score else 0.0

    # Jobs matched
    jobs_matched = (
        db.session.query(func.count(func.distinct(Match.job_id)))
        .join(Resume, Match.resume_id == Resume.id)
        .filter(Resume.user_id == user_id)
        .scalar()
    )
    stats["jobs_matched"] = jobs_matched

    # Total available jobs
    stats["total_jobs"] = Job.query.filter_by(status="active").count()

    # Score breakdown
    excellent = (
        db.session.query(Match)
        .join(Resume, Match.resume_id == Resume.id)
        .filter(Resume.user_id == user_id, Match.overall_score >= 0.75)
        .count()
    )
    good = (
        db.session.query(Match)
        .join(Resume, Match.resume_id == Resume.id)
        .filter(Resume.user_id == user_id, Match.overall_score >= 0.55, Match.overall_score < 0.75)
        .count()
    )
    average = (
        db.session.query(Match)
        .join(Resume, Match.resume_id == Resume.id)
        .filter(Resume.user_id == user_id, Match.overall_score >= 0.40, Match.overall_score < 0.55)
        .count()
    )
    low = (
        db.session.query(Match)
        .join(Resume, Match.resume_id == Resume.id)
        .filter(Resume.user_id == user_id, Match.overall_score < 0.40)
        .count()
    )
    stats["breakdown"] = {
        "excellent": excellent,
        "good": good,
        "average": average,
        "low": low,
    }

    # Top skills from user's resume
    top_skills = (
        db.session.query(Skill.canonical_name, func.count(ResumeSkill.id))
        .join(ResumeSkill, Skill.id == ResumeSkill.skill_id)
        .join(Resume, Resume.id == ResumeSkill.resume_id)
        .filter(Resume.user_id == user_id)
        .group_by(Skill.canonical_name)
        .order_by(func.count(ResumeSkill.id).desc())
        .limit(8)
        .all()
    )
    stats["your_skills"] = [{"skill": s, "count": c} for s, c in top_skills]

    return jsonify(stats), 200


@dashboard_bp.route("/recent-activity", methods=["GET"])
@jwt_required()
def get_recent_activity():
    """Get recent activity for candidates."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    activity = []

    # Recent matches
    recent_matches = (
        db.session.query(Match)
        .join(Resume, Match.resume_id == Resume.id)
        .filter(Resume.user_id == user_id)
        .order_by(Match.created_at.desc())
        .limit(10)
        .all()
    )
    for match in recent_matches:
        score_pct = round(match.overall_score * 100)
        if score_pct >= 75:
            label = "Excellent match"
        elif score_pct >= 55:
            label = "Good match"
        elif score_pct >= 40:
            label = "Moderate match"
        else:
            label = "Low match"
        activity.append({
            "type": "match",
            "description": f"{match.job.title} at {match.job.company}",
            "score": round(match.overall_score, 4),
            "label": label,
            "created_at": match.created_at.isoformat() if match.created_at else None,
        })

    return jsonify({"activity": activity}), 200
