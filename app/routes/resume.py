import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.resume import Resume
from app.models.enums import ResumeStatus
from app.services.resume_service import ResumeService

resume_bp = Blueprint("resume", __name__)
resume_service = ResumeService()


@resume_bp.route("", methods=["POST"])
@jwt_required()
def upload_resume():
    """Upload and process a resume file."""
    user_id = int(get_jwt_identity())

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    original_filename = file.filename
    file_ext = original_filename.rsplit(".", 1)[-1].lower()

    if file_ext not in current_app.config["ALLOWED_EXTENSIONS"]:
        return jsonify({
            "error": f"Unsupported file type: {file_ext}. Allowed: {current_app.config['ALLOWED_EXTENSIONS']}"
        }), 400

    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], str(user_id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)
    file.save(file_path)

    resume = Resume(
        user_id=user_id,
        original_filename=original_filename,
        file_path=file_path,
        file_type=file_ext,
        file_size=os.path.getsize(file_path),
        status=ResumeStatus.UPLOADED,
    )
    db.session.add(resume)
    db.session.commit()

    result = resume_service.process_resume(resume.id)

    return jsonify({
        "message": "Resume uploaded and processed successfully",
        "resume_id": resume.id,
        "status": resume.status.value,
        "extraction_result": result,
    }), 201


@resume_bp.route("", methods=["GET"])
@jwt_required()
def list_resumes():
    """List all resumes for the current user."""
    user_id = int(get_jwt_identity())

    resumes = Resume.query.filter_by(user_id=user_id).order_by(
        Resume.created_at.desc()
    ).all()

    return jsonify({
        "resumes": [
            {
                "id": r.id,
                "filename": r.original_filename,
                "status": r.status.value,
                "file_type": r.file_type,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in resumes
        ],
        "total": len(resumes),
    }), 200


@resume_bp.route("/<int:resume_id>", methods=["GET"])
@jwt_required()
def get_resume(resume_id):
    """Get detailed information about a resume."""
    user_id = int(get_jwt_identity())
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()

    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    details = resume_service.get_resume_details(resume.id)
    return jsonify(details), 200


@resume_bp.route("/<int:resume_id>", methods=["DELETE"])
@jwt_required()
def delete_resume(resume_id):
    """Delete a resume."""
    user_id = int(get_jwt_identity())
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()

    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)

    db.session.delete(resume)
    db.session.commit()

    return jsonify({"message": "Resume deleted successfully"}), 200
