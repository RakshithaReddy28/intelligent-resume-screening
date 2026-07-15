from typing import List, Dict, Tuple
from rapidfuzz import fuzz, process
from dataclasses import dataclass


@dataclass
class SkillMatchResult:
    """Result of skill matching."""
    matched: List[Dict]
    missing: List[str]
    score: float


class SkillMatcher:
    """Match resume skills against job requirements."""

    def __init__(self, fuzzy_threshold: int = 75):
        self.fuzzy_threshold = fuzzy_threshold

    def match(
        self,
        job_skills: List[Dict],
        resume_skills: List[Dict],
    ) -> SkillMatchResult:
        """
        Match resume skills against job requirements.

        Args:
            job_skills: [{"name": "Python", "is_required": true}, ...]
            resume_skills: [{"name": "python", "confidence": 0.95}, ...]

        Returns:
            SkillMatchResult with matched skills, missing skills, and score
        """
        # Normalize resume skills to a set of lowercase names
        resume_skill_names = set()
        resume_skill_map = {}

        for rs in resume_skills:
            name = rs["name"].lower().strip()
            resume_skill_names.add(name)
            resume_skill_map[name] = rs

        matched = []
        missing = []
        required_missing = []

        for js in job_skills:
            job_skill_name = js["name"].lower().strip()
            is_required = js.get("is_required", True)

            # Phase 1: Exact match
            if job_skill_name in resume_skill_names:
                matched.append({
                    "job_skill": js["name"],
                    "resume_skill": resume_skill_map[job_skill_name]["name"],
                    "confidence": resume_skill_map[job_skill_name].get("confidence", 1.0),
                    "match_type": "exact",
                })
                continue

            # Phase 2: Fuzzy match
            result = process.extractOne(
                job_skill_name,
                list(resume_skill_names),
                scorer=fuzz.token_sort_ratio,
            )

            if result and result[1] >= self.fuzzy_threshold:
                matched_canonical = result[0]
                matched.append({
                    "job_skill": js["name"],
                    "resume_skill": resume_skill_map[matched_canonical]["name"],
                    "confidence": resume_skill_map[matched_canonical].get("confidence", 1.0),
                    "match_type": "fuzzy",
                    "fuzzy_score": result[1] / 100.0,
                })
            else:
                missing.append(js["name"])
                if is_required:
                    required_missing.append(js["name"])

        # Calculate skill score
        total_required = sum(1 for js in job_skills if js.get("is_required", True))
        matched_required = total_required - len(required_missing)
        total_skills = len(job_skills)

        if total_skills == 0:
            score = 1.0
        else:
            # Required skills weighted more heavily
            required_ratio = matched_required / total_required if total_required > 0 else 1.0
            overall_ratio = len(matched) / total_skills
            # 70% weight on required, 30% on overall coverage
            score = 0.7 * required_ratio + 0.3 * overall_ratio

        return SkillMatchResult(
            matched=matched,
            missing=missing,
            score=round(min(score, 1.0), 4),
        )
