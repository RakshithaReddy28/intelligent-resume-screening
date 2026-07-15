import re
import json
import os
from typing import List, Dict, Tuple


class SkillExtractor:
    """Extract skills from resume text using pattern matching and NLP."""

    def __init__(self):
        self.skill_database = self._load_skill_database()
        self.skill_patterns = self._build_patterns()

    def _load_skill_database(self) -> Dict:
        """Load the skill taxonomy from JSON file."""
        default_skills = {
            "programming": [
                "python", "java", "javascript", "typescript", "c++", "c#", "ruby",
                "php", "swift", "kotlin", "go", "rust", "scala", "r", "matlab",
                "sql", "html", "css", "react", "angular", "vue", "node.js",
                "django", "flask", "fastapi", "spring", "rails", "laravel",
            ],
            "data_science": [
                "machine learning", "deep learning", "natural language processing",
                "nlp", "computer vision", "tensorflow", "pytorch", "keras",
                "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn",
                "data analysis", "data visualization", "statistical modeling",
                "neural networks", "transformers", "bert", "gpt",
            ],
            "cloud_devops": [
                "aws", "azure", "gcp", "docker", "kubernetes", "jenkins",
                "ci/cd", "terraform", "ansible", "chef", "puppet", "git",
                "github", "gitlab", "bitbucket", "linux", "bash", "powershell",
            ],
            "databases": [
                "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
                "cassandra", "dynamodb", "sqlite", "oracle", "sql server",
                "neo4j", "couchdb",
            ],
            "soft_skills": [
                "leadership", "communication", "teamwork", "problem solving",
                "critical thinking", "time management", "project management",
                "agile", "scrum", "collaboration", "mentoring",
            ],
        }

        # Try to load from file if exists
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        taxonomy_path = os.path.join(data_dir, "skills_taxonomy.json")

        if os.path.exists(taxonomy_path):
            with open(taxonomy_path, "r") as f:
                return json.load(f)

        return default_skills

    def _build_patterns(self) -> List[Tuple[str, str, str]]:
        """Build regex patterns for skill matching."""
        patterns = []

        for category, skills in self.skill_database.items():
            for skill in skills:
                # Create pattern that matches the skill word boundary
                escaped = re.escape(skill)
                pattern = r"\b" + escaped + r"\b"
                patterns.append((pattern, skill, category))

        return patterns

    def extract_skills(self, text: str) -> List[Dict]:
        """Extract skills from text."""
        found_skills = []
        text_lower = text.lower()

        for pattern, skill_name, category in self.skill_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                # Calculate confidence based on context
                confidence = self._calculate_confidence(text, match.start(), skill_name)

                found_skills.append({
                    "name": skill_name,
                    "category": category,
                    "confidence": confidence,
                    "start_pos": match.start(),
                    "end_pos": match.end(),
                })

        # Remove duplicates and sort by confidence
        unique_skills = self._deduplicate_skills(found_skills)
        return sorted(unique_skills, key=lambda x: x["confidence"], reverse=True)

    def _calculate_confidence(self, text: str, position: int, skill: str) -> float:
        """Calculate confidence score based on context."""
        # Get surrounding context (100 chars before and after)
        start = max(0, position - 100)
        end = min(len(text), position + len(skill) + 100)
        context = text[start:end].lower()

        # Higher confidence if near action verbs or in skills section
        high_confidence_indicators = [
            "proficient in", "experience with", "skilled in",
            "knowledge of", "familiar with", "expertise in",
            "skills:", "technologies:", "tools:",
        ]

        confidence = 0.7  # Base confidence

        for indicator in high_confidence_indicators:
            if indicator in context:
                confidence = min(1.0, confidence + 0.15)

        return round(confidence, 2)

    def _deduplicate_skills(self, skills: List[Dict]) -> List[Dict]:
        """Remove duplicate skills, keeping highest confidence."""
        seen = {}
        for skill in skills:
            name = skill["name"]
            if name not in seen or skill["confidence"] > seen[name]["confidence"]:
                seen[name] = skill

        return list(seen.values())

    def extract_from_section(self, text: str, section_name: str) -> List[Dict]:
        """Extract skills from a specific section of the resume."""
        # Find the section
        section_pattern = rf"(?:{section_name}|skills|technologies)[:\s]*\n(.*?)(?:\n\n|\Z)"
        match = re.search(section_pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            section_text = match.group(1)
            return self.extract_skills(section_text)

        return self.extract_skills(text)
