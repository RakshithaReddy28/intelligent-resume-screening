from typing import List, Dict
from app.models.match import Match
from app.models.enums import MatchStatus
from app.extensions import db


class ShortlistingService:
    """Auto-shortlist and recommend candidates based on match scores."""

    # Configurable thresholds
    DEFAULT_THRESHOLDS = {
        "automatic_shortlist": 0.75,
        "review_recommended": 0.55,
        "borderline": 0.40,
    }

    def get_recommendations(self, job_id: int, recruiter_id: int, thresholds: dict = None) -> Dict:
        """
        Get shortlisting recommendations for a job.

        Returns categorized candidates:
        - auto_shortlist: Score >= 75% (auto-shortlist)
        - recommended: 55-75% (review recommended)
        - borderline: 40-55% (borderline)
        - not_recommended: < 40%
        """
        t = thresholds or self.DEFAULT_THRESHOLDS

        matches = Match.query.filter_by(
            job_id=job_id,
            recruiter_id=recruiter_id,
            status=MatchStatus.COMPLETED,
        ).order_by(Match.overall_score.desc()).all()

        categories = {
            "auto_shortlist": [],
            "recommended": [],
            "borderline": [],
            "not_recommended": [],
        }

        stats = {
            "total_candidates": len(matches),
            "auto_shortlist_count": 0,
            "recommended_count": 0,
            "borderline_count": 0,
            "not_recommended_count": 0,
            "average_score": 0.0,
            "top_skill_gaps": {},
        }

        if not matches:
            return {"categories": categories, "stats": stats}

        total_score = 0
        skill_gap_count = {}

        for match in matches:
            score = match.overall_score
            total_score += score

            entry = {
                "match_id": match.id,
                "resume_id": match.resume_id,
                "candidate_name": f"{match.resume.owner.first_name} {match.resume.owner.last_name}",
                "candidate_email": match.resume.owner.email,
                "resume_filename": match.resume.original_filename,
                "overall_score": round(score, 4),
                "skill_score": round(match.skill_score, 4),
                "experience_score": round(match.experience_score, 4),
                "education_score": round(match.education_score, 4),
                "semantic_score": round(match.semantic_score, 4),
                "matched_skills": match.matched_skills or [],
                "missing_skills": match.missing_skills or [],
                "explanation": match.explanation or "",
                "recommendation": "",
            }

            # Categorize
            if score >= t["automatic_shortlist"]:
                entry["recommendation"] = "AUTO-SHORTLIST: Strong candidate, proceed to interview."
                categories["auto_shortlist"].append(entry)
                stats["auto_shortlist_count"] += 1
            elif score >= t["review_recommended"]:
                entry["recommendation"] = "RECOMMENDED: Good candidate, worth reviewing."
                categories["recommended"].append(entry)
                stats["recommended_count"] += 1
            elif score >= t["borderline"]:
                entry["recommendation"] = "BORDERLINE: May need additional screening."
                categories["borderline"].append(entry)
                stats["borderline_count"] += 1
            else:
                entry["recommendation"] = "NOT RECOMMENDED: Does not meet minimum requirements."
                categories["not_recommended"].append(entry)
                stats["not_recommended_count"] += 1

            # Track skill gaps
            for skill in match.missing_skills or []:
                skill_lower = skill.lower()
                skill_gap_count[skill_lower] = skill_gap_count.get(skill_lower, 0) + 1

        stats["average_score"] = round(total_score / len(matches), 4) if matches else 0

        # Top skill gaps (most commonly missing)
        sorted_gaps = sorted(skill_gap_count.items(), key=lambda x: x[1], reverse=True)
        stats["top_skill_gaps"] = [{"skill": s, "count": c} for s, c in sorted_gaps[:5]]

        return {"categories": categories, "stats": stats}

    def auto_shortlist(self, job_id: int, recruiter_id: int, threshold: float = 0.75) -> List[Dict]:
        """Get list of candidates that meet the auto-shortlist threshold."""
        matches = Match.query.filter(
            Match.job_id == job_id,
            Match.recruiter_id == recruiter_id,
            Match.status == MatchStatus.COMPLETED,
            Match.overall_score >= threshold,
        ).order_by(Match.overall_score.desc()).all()

        return [
            {
                "match_id": m.id,
                "candidate_name": f"{m.resume.owner.first_name} {m.resume.owner.last_name}",
                "candidate_email": m.resume.owner.email,
                "score": round(m.overall_score, 4),
            }
            for m in matches
        ]

    def get_skill_gap_analysis(self, job_id: int, recruiter_id: int) -> Dict:
        """Analyze common skill gaps across all candidates for a job."""
        matches = Match.query.filter_by(
            job_id=job_id,
            recruiter_id=recruiter_id,
            status=MatchStatus.COMPLETED,
        ).all()

        all_matched = {}
        all_missing = {}
        total = len(matches)

        for match in matches:
            for skill_entry in match.matched_skills or []:
                name = skill_entry.get("job_skill", "").lower()
                if name:
                    all_matched[name] = all_matched.get(name, 0) + 1

            for skill in match.missing_skills or []:
                name = skill.lower()
                if name:
                    all_missing[name] = all_missing.get(name, 0) + 1

        return {
            "total_candidates": total,
            "skill_coverage": [
                {"skill": s, "matched": c, "coverage": round(c / total * 100, 1) if total else 0}
                for s, c in sorted(all_matched.items(), key=lambda x: x[1], reverse=True)
            ],
            "skill_gaps": [
                {"skill": s, "missing": c, "gap_percentage": round(c / total * 100, 1) if total else 0}
                for s, c in sorted(all_missing.items(), key=lambda x: x[1], reverse=True)
            ],
        }
