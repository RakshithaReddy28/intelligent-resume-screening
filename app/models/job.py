from datetime import datetime, timezone
from app.extensions import db
from app.models.enums import JobStatus


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255), nullable=True)
    job_type = db.Column(db.String(50), nullable=True)  # full-time, part-time, contract
    experience_min_years = db.Column(db.Float, nullable=True)
    experience_max_years = db.Column(db.Float, nullable=True)
    education_level = db.Column(db.String(100), nullable=True)
    status = db.Column(
        db.Enum(JobStatus), default=JobStatus.DRAFT, nullable=False
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    skills = db.relationship(
        "JobSkill", backref="job", lazy="dynamic", cascade="all, delete-orphan"
    )
    matches = db.relationship(
        "Match", backref="job", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Job {self.title}>"


class JobSkill(db.Model):
    __tablename__ = "job_skills"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    is_required = db.Column(db.Boolean, nullable=False, default=True)

    skill = db.relationship("Skill", backref="job_skill_links")
