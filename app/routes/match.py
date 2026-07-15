from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.match import Match
from app.models.resume import Resume
from app.models.job import Job
from app.models.enums import MatchStatus, UserRole, JobStatus
from app.models.user import User
from app.ml.ranking import MatchingService
from app.ml.classifier import ResumeClassifier
from app.services.shortlisting_service import ShortlistingService

match_bp = Blueprint("match", __name__)
matching_service = MatchingService()
resume_classifier = ResumeClassifier()
shortlisting_service = ShortlistingService()


@match_bp.route("/auto-match", methods=["POST"])
@jwt_required()
def auto_match_resume():
    """Auto-match the user's latest resume against all active jobs."""
    user_id = int(get_jwt_identity())

    resumes = Resume.query.filter_by(user_id=user_id, status="parsed").order_by(
        Resume.created_at.desc()
    ).all()
    if not resumes:
        return jsonify({"error": "No parsed resumes found. Upload a resume first."}), 400

    resume = resumes[0]
    jobs = Job.query.filter_by(status=JobStatus.ACTIVE).all()
    if not jobs:
        return jsonify({"error": "No active jobs available."}), 400

    matches_created = 0
    for job in jobs:
        existing = Match.query.filter_by(job_id=job.id, resume_id=resume.id).first()
        if existing:
            result = matching_service.match_job_to_resume(job, resume)
            existing.overall_score = result["overall_score"]
            existing.skill_score = result["skill_score"]
            existing.experience_score = result["experience_score"]
            existing.education_score = result["education_score"]
            existing.semantic_score = result["semantic_score"]
            existing.matched_skills = result["matched_skills"]
            existing.missing_skills = result["missing_skills"]
            existing.explanation = result["explanation"]
            existing.status = MatchStatus.COMPLETED
        else:
            result = matching_service.match_job_to_resume(job, resume)
            match = Match(
                job_id=job.id,
                resume_id=resume.id,
                recruiter_id=job.recruiter_id,
                overall_score=result["overall_score"],
                skill_score=result["skill_score"],
                experience_score=result["experience_score"],
                education_score=result["education_score"],
                semantic_score=result["semantic_score"],
                matched_skills=result["matched_skills"],
                missing_skills=result["missing_skills"],
                explanation=result["explanation"],
                status=MatchStatus.COMPLETED,
            )
            db.session.add(match)
        matches_created += 1

    db.session.commit()
    return jsonify({
        "message": f"Matched against {matches_created} jobs",
        "resume_id": resume.id,
        "total_matched": matches_created,
    }), 200


@match_bp.route("/my-matches", methods=["GET"])
@jwt_required()
def get_my_matches():
    """Get all matches for the current user's resumes, ranked by score."""
    user_id = int(get_jwt_identity())

    matches = (
        db.session.query(Match)
        .join(Resume, Match.resume_id == Resume.id)
        .filter(Resume.user_id == user_id)
        .order_by(Match.overall_score.desc())
        .all()
    )

    results = []
    for i, match in enumerate(matches, 1):
        job = match.job
        job_skills = []
        for js in job.skills:
            job_skills.append({
                "name": js.skill.canonical_name,
                "is_required": js.is_required,
            })

        results.append({
            "rank": i,
            "match_id": match.id,
            "job": {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "job_type": job.job_type,
                "experience_range": f"{job.experience_min_years or 0}-{job.experience_max_years or '?'} years",
                "education_level": job.education_level,
                "skills": job_skills,
            },
            "resume": {
                "id": match.resume.id,
                "filename": match.resume.original_filename,
            },
            "scores": {
                "overall": round(match.overall_score, 4),
                "skill": round(match.skill_score, 4),
                "experience": round(match.experience_score, 4),
                "education": round(match.education_score, 4),
                "semantic": round(match.semantic_score, 4),
            },
            "matched_skills": match.matched_skills or [],
            "missing_skills": match.missing_skills or [],
            "explanation": match.explanation,
            "created_at": match.created_at.isoformat() if match.created_at else None,
        })

    return jsonify({"matches": results, "total": len(results)}), 200


@match_bp.route("/classify/<int:resume_id>", methods=["GET"])
@jwt_required()
def classify_resume(resume_id):
    """Classify a resume into job roles."""
    user_id = int(get_jwt_identity())
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()

    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    skills = []
    for rs in resume.skills:
        skills.append({"name": rs.skill.canonical_name})

    experience = []
    for exp in resume.experiences:
        experience.append({"title": exp.title, "company": exp.company, "duration_months": exp.duration_months})

    classifications = resume_classifier.classify(
        skills=skills,
        experience=experience,
        raw_text=resume.raw_text or "",
    )

    return jsonify({
        "resume_id": resume_id,
        "filename": resume.original_filename,
        "classifications": classifications,
    }), 200


@match_bp.route("/job/<int:job_id>", methods=["POST"])
@jwt_required()
def run_matching(job_id):
    """Trigger matching of all resumes against a job (recruiter only)."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if user.role != UserRole.RECRUITER:
        return jsonify({"error": "Only recruiters can run matching"}), 403

    try:
        matches = matching_service.match_job_to_all_resumes(job_id, user_id)
        return jsonify({
            "message": f"Matching completed. {len(matches)} resumes evaluated.",
            "job_id": job_id,
            "total_matches": len(matches),
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Matching failed: {str(e)}"}), 500


@match_bp.route("/job/<int:job_id>", methods=["GET"])
@jwt_required()
def get_match_results(job_id):
    """Get ranked match results for a job."""
    user_id = int(get_jwt_identity())

    matches = (
        Match.query
        .filter(Match.job_id == job_id)
        .order_by(Match.overall_score.desc())
        .all()
    )

    results = []
    for i, match in enumerate(matches, 1):
        results.append({
            "rank": i,
            "match_id": match.id,
            "resume_id": match.resume_id,
            "candidate": {
                "name": f"{match.resume.owner.first_name} {match.resume.owner.last_name}",
                "email": match.resume.owner.email,
            },
            "resume": {"filename": match.resume.original_filename},
            "scores": {
                "overall": round(match.overall_score, 4),
                "skill": round(match.skill_score, 4),
                "experience": round(match.experience_score, 4),
                "education": round(match.education_score, 4),
                "semantic": round(match.semantic_score, 4),
            },
            "matched_skills": match.matched_skills,
            "missing_skills": match.missing_skills,
            "explanation": match.explanation,
        })

    return jsonify({"job_id": job_id, "results": results, "total": len(results)}), 200
