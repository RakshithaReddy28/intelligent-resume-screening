from datetime import datetime, timezone
from app.extensions import db
from app.models.enums import MatchStatus


class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    recruiter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Scores (0.0 - 1.0)
    overall_score = db.Column(db.Float, nullable=False, index=True)
    skill_score = db.Column(db.Float, nullable=False)
    experience_score = db.Column(db.Float, nullable=False)
    education_score = db.Column(db.Float, nullable=False)
    semantic_score = db.Column(db.Float, nullable=False)

    # Details
    matched_skills = db.Column(db.JSON, nullable=True)
    missing_skills = db.Column(db.JSON, nullable=True)
    explanation = db.Column(db.Text, nullable=True)

    status = db.Column(
        db.Enum(MatchStatus), default=MatchStatus.PENDING, nullable=False
    )
    rank_position = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    resume = db.relationship("Resume", backref="match_results")
    recruiter = db.relationship("User", backref="match_results")

    # One match per job-resume pair
    __table_args__ = (
        db.UniqueConstraint("job_id", "resume_id", name="uq_job_resume_match"),
    )

    def __repr__(self):
        return f"<Match job={self.job_id} resume={self.resume_id} score={self.overall_score}>"
