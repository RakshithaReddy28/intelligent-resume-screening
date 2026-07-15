from typing import Dict, List


class ResumeClassifier:
    """Classify resumes into job roles based on extracted skills and experience."""

    JOB_ROLE_PROFILES = {
        "Software Developer": {
            "required_skills": ["python", "java", "javascript", "c++", "git"],
            "preferred_skills": ["react", "angular", "django", "flask", "sql", "html", "css"],
            "keywords": ["software", "developer", "programming", "backend", "frontend", "full stack"],
            "weight": 1.0,
        },
        "Data Scientist": {
            "required_skills": ["python", "machine learning", "statistics"],
            "preferred_skills": ["tensorflow", "pytorch", "deep learning", "nlp", "pandas", "numpy", "scikit-learn"],
            "keywords": ["data science", "machine learning", "artificial intelligence", "analytics", "modeling"],
            "weight": 1.0,
        },
        "Data Analyst": {
            "required_skills": ["sql", "python", "excel"],
            "preferred_skills": ["tableau", "power bi", "pandas", "statistics", "data visualization"],
            "keywords": ["data analysis", "reporting", "analytics", "business intelligence", "dashboard"],
            "weight": 0.9,
        },
        "Web Developer": {
            "required_skills": ["javascript", "html", "css"],
            "preferred_skills": ["react", "angular", "vue", "node.js", "php", "django"],
            "keywords": ["web", "frontend", "backend", "full stack", "responsive"],
            "weight": 1.0,
        },
        "DevOps Engineer": {
            "required_skills": ["linux", "docker", "git"],
            "preferred_skills": ["kubernetes", "aws", "azure", "terraform", "jenkins", "ci/cd", "ansible"],
            "keywords": ["devops", "infrastructure", "deployment", "cloud", "automation", "ci/cd"],
            "weight": 1.0,
        },
        "Cloud Engineer": {
            "required_skills": ["aws", "linux"],
            "preferred_skills": ["azure", "gcp", "docker", "kubernetes", "terraform"],
            "keywords": ["cloud", "aws", "azure", "gcp", "infrastructure", "saas"],
            "weight": 1.0,
        },
        "Mobile Developer": {
            "required_skills": ["swift", "kotlin", "java"],
            "preferred_skills": ["flutter", "react native", "ios", "android"],
            "keywords": ["mobile", "ios", "android", "app", "flutter"],
            "weight": 1.0,
        },
        "Machine Learning Engineer": {
            "required_skills": ["python", "machine learning", "deep learning"],
            "preferred_skills": ["tensorflow", "pytorch", "keras", "nlp", "computer vision"],
            "keywords": ["machine learning", "deep learning", "ai", "neural network", "model"],
            "weight": 1.0,
        },
        "Database Administrator": {
            "required_skills": ["sql", "mysql", "postgresql"],
            "preferred_skills": ["mongodb", "oracle", "sql server", "redis", "elasticsearch"],
            "keywords": ["database", "dba", "admin", "backup", "optimization"],
            "weight": 0.9,
        },
        "Project Manager": {
            "required_skills": ["project management", "agile", "scrum"],
            "preferred_skills": ["jira", "leadership", "communication", "risk management"],
            "keywords": ["project management", "scrum master", "product owner", "delivery"],
            "weight": 0.9,
        },
        "QA Engineer": {
            "required_skills": ["testing", "selenium"],
            "preferred_skills": ["automation", "python", "java", "junit", "cypress"],
            "keywords": ["quality assurance", "testing", "automation", "qa", "test engineer"],
            "weight": 0.8,
        },
    }

    def classify(self, skills: List[Dict], experience: List[Dict] = None, raw_text: str = "") -> List[Dict]:
        """
        Classify a resume into job roles with confidence scores.

        Returns sorted list of {"role": ..., "confidence": ..., "matched_skills": ...}
        """
        skill_names = set()
        for s in skills:
            skill_names.add(s.get("name", "").lower())

        text_lower = raw_text.lower() if raw_text else ""
        results = []

        for role, profile in self.JOB_ROLE_PROFILES.items():
            score, matched = self._score_role(skill_names, text_lower, profile)
            if score > 0.05:
                results.append({
                    "role": role,
                    "confidence": round(min(score, 1.0), 4),
                    "matched_skills": matched,
                })

        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results[:5]

    def _score_role(self, skill_names: set, text_lower: str, profile: Dict) -> tuple:
        """Score how well a resume matches a job role."""
        matched = []
        required_score = 0
        preferred_score = 0

        for skill in profile["required_skills"]:
            if skill in skill_names:
                required_score += 1
                matched.append(skill)

        for skill in profile["preferred_skills"]:
            if skill in skill_names:
                preferred_score += 1
                matched.append(skill)

        # Keyword bonus
        keyword_hits = 0
        for kw in profile["keywords"]:
            if kw in text_lower:
                keyword_hits += 1

        total_required = len(profile["required_skills"])
        total_preferred = len(profile["preferred_skills"])

        req_ratio = required_score / total_required if total_required > 0 else 0
        pref_ratio = preferred_score / total_preferred if total_preferred > 0 else 0
        kw_ratio = min(keyword_hits / max(len(profile["keywords"]), 1), 1.0)

        # 50% required skills, 30% preferred, 20% keywords
        score = (0.5 * req_ratio + 0.3 * pref_ratio + 0.2 * kw_ratio) * profile["weight"]

        return score, matched
