from datetime import datetime, timezone
from app.extensions import db
from app.models.enums import ResumeStatus


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # pdf, docx, txt
    file_size = db.Column(db.Integer, nullable=False)
    raw_text = db.Column(db.Text, nullable=True)
    parsed_json = db.Column(db.JSON, nullable=True)
    status = db.Column(
        db.Enum(ResumeStatus), default=ResumeStatus.UPLOADED, nullable=False
    )
    parsing_error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    educations = db.relationship(
        "ResumeEducation", backref="resume", lazy="dynamic", cascade="all, delete-orphan"
    )
    experiences = db.relationship(
        "ResumeExperience", backref="resume", lazy="dynamic", cascade="all, delete-orphan"
    )
    skills = db.relationship(
        "ResumeSkill", backref="resume", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Resume {self.original_filename}>"


class ResumeEducation(db.Model):
    __tablename__ = "resume_educations"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    institution = db.Column(db.String(255), nullable=True)
    degree = db.Column(db.String(255), nullable=True)
    field_of_study = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)


class ResumeExperience(db.Model):
    __tablename__ = "resume_experiences"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    company = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    is_current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, nullable=True)
    duration_months = db.Column(db.Integer, nullable=True)


class ResumeSkill(db.Model):
    __tablename__ = "resume_skills"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    confidence = db.Column(db.Float, default=1.0)

    skill = db.relationship("Skill", backref="resume_skill_links")
