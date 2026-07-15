from typing import List, Dict, Optional
from datetime import date
from app.ml.matcher import SkillMatcher
from app.ml.vectorizer import TextVectorizer
from app.extensions import db
from app.models.resume import Resume
from app.models.job import Job
from app.models.match import Match
from app.models.enums import MatchStatus


class MatchingService:
    """Orchestrates the full matching pipeline."""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.weights = self.config.get("MATCH_WEIGHTS", {
            "skill": 0.40,
            "experience": 0.30,
            "education": 0.10,
            "semantic": 0.20,
        })
        self.skill_matcher = SkillMatcher()
        self.vectorizer = TextVectorizer()

    def match_job_to_resume(self, job: Job, resume: Resume) -> Dict:
        """
        Match a single resume against a job description.

        Returns:
            Dictionary with match scores and details
        """
        # Get resume data
        resume_data = self._get_resume_data(resume)

        # Get job requirements
        job_skills = self._get_job_skills(job)

        # 1. Skill matching
        skill_result = self.skill_matcher.match(job_skills, resume_data["skills"])

        # 2. Experience matching
        experience_score, experience_explanation = self._match_experience(
            job.experience_min_years,
            job.experience_max_years,
            resume_data["total_experience_months"],
        )

        # 3. Education matching
        education_score, education_explanation = self._match_education(
            job.education_level,
            resume_data["education"],
        )

        # 4. Semantic similarity
        semantic_score = self._compute_semantic_similarity(
            job.description,
            resume.raw_text or "",
        )

        # Calculate overall score
        overall_score = (
            self.weights["skill"] * skill_result.score +
            self.weights["experience"] * experience_score +
            self.weights["education"] * education_score +
            self.weights["semantic"] * semantic_score
        )

        # Build explanation
        explanation = self._build_explanation(
            skill_result,
            experience_explanation,
            education_explanation,
            overall_score,
        )

        return {
            "overall_score": round(min(overall_score, 1.0), 4),
            "skill_score": skill_result.score,
            "experience_score": experience_score,
            "education_score": education_score,
            "semantic_score": semantic_score,
            "matched_skills": skill_result.matched,
            "missing_skills": skill_result.missing,
            "explanation": explanation,
        }

    def match_job_to_all_resumes(self, job_id: int, recruiter_id: int) -> List[Match]:
        """Match all active resumes against a job."""
        job = Job.query.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Get all parsed resumes
        resumes = Resume.query.filter_by(status="parsed").all()

        matches = []
        for resume in resumes:
            # Check if match already exists
            existing_match = Match.query.filter_by(
                job_id=job_id,
                resume_id=resume.id,
            ).first()

            if existing_match:
                # Update existing match
                result = self.match_job_to_resume(job, resume)
                existing_match.overall_score = result["overall_score"]
                existing_match.skill_score = result["skill_score"]
                existing_match.experience_score = result["experience_score"]
                existing_match.education_score = result["education_score"]
                existing_match.semantic_score = result["semantic_score"]
                existing_match.matched_skills = result["matched_skills"]
                existing_match.missing_skills = result["missing_skills"]
                existing_match.explanation = result["explanation"]
                existing_match.status = MatchStatus.COMPLETED
                matches.append(existing_match)
            else:
                # Create new match
                result = self.match_job_to_resume(job, resume)
                match = Match(
                    job_id=job_id,
                    resume_id=resume.id,
                    recruiter_id=recruiter_id,
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
                matches.append(match)

        db.session.commit()

        # Rank matches
        self._rank_matches(matches)

        return matches

    def _get_resume_data(self, resume: Resume) -> Dict:
        """Extract structured data from resume."""
        skills = []
        total_experience_months = 0
        education = []

        # Get skills from parsed data or skill relationships
        if resume.parsed_json and "skills" in resume.parsed_json:
            skills = resume.parsed_json["skills"]
        else:
            for rs in resume.skills:
                skills.append({
                    "name": rs.skill.canonical_name,
                    "confidence": rs.confidence,
                })

        # Get experience
        for exp in resume.experiences:
            if exp.duration_months:
                total_experience_months += exp.duration_months

        # Get education
        for edu in resume.educations:
            education.append({
                "institution": edu.institution,
                "degree": edu.degree,
                "field_of_study": edu.field_of_study,
            })

        return {
            "skills": skills,
            "total_experience_months": total_experience_months,
            "education": education,
        }

    def _get_job_skills(self, job: Job) -> List[Dict]:
        """Get required skills for a job."""
        skills = []
        for js in job.skills:
            skills.append({
                "name": js.skill.canonical_name,
                "is_required": js.is_required,
            })
        return skills

    def _match_experience(
        self,
        min_years: Optional[float],
        max_years: Optional[float],
        candidate_months: int,
    ) -> tuple:
        """Match experience requirements."""
        candidate_years = candidate_months / 12.0

        if min_years is None and max_years is None:
            return 0.7, "No specific experience requirement."

        min_years = min_years or 0
        max_years = max_years or min_years + 10

        if candidate_years >= min_years:
            if candidate_years <= max_years:
                score = 1.0
            else:
                over_years = candidate_years - max_years
                score = max(0.7, 1.0 - (over_years * 0.02))
            explanation = f"Candidate has {candidate_years:.1f} years (target: {min_years}-{max_years})."
        else:
            if min_years == 0:
                score = 1.0
            else:
                score = max(0.0, candidate_years / min_years)
            explanation = f"Candidate has {candidate_years:.1f} years (minimum: {min_years})."

        return round(min(score, 1.0), 4), explanation

    def _match_education(
        self,
        required_level: Optional[str],
        educations: List[Dict],
    ) -> tuple:
        """Match education requirements."""
        degree_rank = {
            "high_school": 1,
            "associate": 2,
            "bachelors": 3,
            "bachelor": 3,
            "master": 4,
            "masters": 4,
            "mba": 4,
            "phd": 5,
            "doctorate": 5,
        }

        if required_level is None:
            return 0.7, "No education requirement specified."

        required_rank = degree_rank.get(required_level.lower(), 0)
        if required_rank == 0:
            return 0.7, f"Unknown requirement: {required_level}"

        # Find highest degree held
        highest_rank = 0
        highest_degree = "none"
        for edu in educations:
            degree = (edu.get("degree") or "").lower()
            for keyword, rank in degree_rank.items():
                if keyword in degree:
                    if rank > highest_rank:
                        highest_rank = rank
                        highest_degree = edu.get("degree", keyword)

        if highest_rank >= required_rank:
            score = 1.0
            explanation = f"Candidate holds {highest_degree} (requires {required_level})."
        elif highest_rank == required_rank - 1:
            score = 0.6
            explanation = f"Candidate holds {highest_degree}, one level below {required_level}."
        else:
            score = max(0.1, highest_rank / required_rank) if required_rank > 0 else 0.1
            explanation = f"Candidate holds {highest_degree}, below required {required_level}."

        return round(score, 4), explanation

    def _compute_semantic_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between two texts."""
        if not text1 or not text2:
            return 0.5

        return self.vectorizer.compute_similarity(text1, text2)

    def _build_explanation(
        self,
        skill_result,
        experience_explanation: str,
        education_explanation: str,
        overall_score: float,
    ) -> str:
        """Build human-readable explanation."""
        parts = []

        # Overall assessment
        if overall_score >= 0.8:
            parts.append("Strong match overall.")
        elif overall_score >= 0.6:
            parts.append("Good match with some gaps.")
        elif overall_score >= 0.4:
            parts.append("Moderate match, significant gaps.")
        else:
            parts.append("Weak match.")

        # Skills summary
        if skill_result.matched:
            parts.append(f"Matches {len(skill_result.matched)} skills.")
        if skill_result.missing:
            parts.append(f"Missing {len(skill_result.missing)} skills: {', '.join(skill_result.missing[:3])}.")

        # Experience
        parts.append(experience_explanation)

        # Education
        parts.append(education_explanation)

        return " ".join(parts)

    def _rank_matches(self, matches: List[Match]):
        """Assign rank positions to matches."""
        sorted_matches = sorted(matches, key=lambda m: m.overall_score, reverse=True)
        for i, match in enumerate(sorted_matches, 1):
            match.rank_position = i
        db.session.commit()
