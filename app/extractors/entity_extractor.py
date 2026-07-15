from typing import Dict, List
from app.extractors.skill_extractor import SkillExtractor
from app.extractors.education_extractor import EducationExtractor
from app.extractors.experience_extractor import ExperienceExtractor


class EntityExtractor:
    """Main entity extractor that combines all extractors."""

    def __init__(self):
        self.skill_extractor = SkillExtractor()
        self.education_extractor = EducationExtractor()
        self.experience_extractor = ExperienceExtractor()

    def extract_all(self, text: str) -> Dict:
        """Extract all entities from resume text."""
        return {
            "skills": self.skill_extractor.extract_skills(text),
            "education": self.education_extractor.extract_education(text),
            "experience": self.experience_extractor.extract_experience(text),
            "raw_text": text,
        }

    def extract_skills(self, text: str) -> List[Dict]:
        """Extract skills only."""
        return self.skill_extractor.extract_skills(text)

    def extract_education(self, text: str) -> List[Dict]:
        """Extract education only."""
        return self.education_extractor.extract_education(text)

    def extract_experience(self, text: str) -> List[Dict]:
        """Extract experience only."""
        return self.experience_extractor.extract_experience(text)
