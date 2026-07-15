import os
from typing import Dict, Optional
from app.parsers.parser_factory import ParserFactory
from app.extractors.entity_extractor import EntityExtractor
from app.models.resume import Resume, ResumeEducation, ResumeExperience, ResumeSkill
from app.models.skill import Skill
from app.models.enums import ResumeStatus
from app.extensions import db


class ResumeService:
    """Service for processing and managing resumes."""

    def __init__(self):
        self.extractor = EntityExtractor()

    def process_resume(self, resume_id: int) -> Dict:
        """
        Process a resume: parse, extract entities, and store results.

        Args:
            resume_id: ID of the resume to process

        Returns:
            Dictionary with processing results
        """
        resume = Resume.query.get(resume_id)
        if not resume:
            raise ValueError(f"Resume {resume_id} not found")

        try:
            # Update status
            resume.status = ResumeStatus.PARSING
            db.session.commit()

            # Parse the file
            parser = ParserFactory.get_parser(resume.file_type)
            raw_text = parser.parse(resume.file_path)
            resume.raw_text = raw_text

            # Extract entities
            extracted_data = self.extractor.extract_all(raw_text)

            # Store extracted data
            resume.parsed_json = {
                "skills": extracted_data["skills"],
                "education": extracted_data["education"],
                "experience": extracted_data["experience"],
            }

            # Create skill relationships
            self._store_skills(resume, extracted_data["skills"])

            # Store education
            self._store_education(resume, extracted_data["education"])

            # Store experience
            self._store_experience(resume, extracted_data["experience"])

            # Update status
            resume.status = ResumeStatus.PARSED
            db.session.commit()

            return {
                "success": True,
                "resume_id": resume.id,
                "skills_found": len(extracted_data["skills"]),
                "education_found": len(extracted_data["education"]),
                "experience_found": len(extracted_data["experience"]),
            }

        except Exception as e:
            resume.status = ResumeStatus.FAILED
            resume.parsing_error = str(e)
            db.session.commit()

            return {
                "success": False,
                "resume_id": resume.id,
                "error": str(e),
            }

    def _store_skills(self, resume: Resume, skills: list):
        """Store extracted skills and create relationships."""
        for skill_data in skills:
            skill_name = skill_data["name"]
            confidence = skill_data.get("confidence", 1.0)

            # Find or create skill
            skill = Skill.query.filter(
                db.func.lower(Skill.canonical_name) == skill_name.lower()
            ).first()

            if not skill:
                skill = Skill(
                    name=skill_name,
                    canonical_name=skill_name.lower(),
                    category=skill_data.get("category", "general"),
                )
                db.session.add(skill)
                db.session.flush()

            # Create relationship
            resume_skill = ResumeSkill(
                resume_id=resume.id,
                skill_id=skill.id,
                confidence=confidence,
            )
            db.session.add(resume_skill)

    def _store_education(self, resume: Resume, educations: list):
        """Store extracted education entries."""
        for edu_data in educations:
            education = ResumeEducation(
                resume_id=resume.id,
                institution=edu_data.get("institution"),
                degree=edu_data.get("degree"),
                field_of_study=edu_data.get("field_of_study"),
                start_date=edu_data.get("start_date"),
                end_date=edu_data.get("end_date"),
                description=edu_data.get("description"),
            )
            db.session.add(education)

    def _store_experience(self, resume: Resume, experiences: list):
        """Store extracted experience entries."""
        for exp_data in experiences:
            experience = ResumeExperience(
                resume_id=resume.id,
                company=exp_data.get("company"),
                title=exp_data.get("title"),
                location=exp_data.get("location"),
                start_date=exp_data.get("start_date"),
                end_date=exp_data.get("end_date"),
                is_current=exp_data.get("is_current", False),
                description=exp_data.get("description"),
                duration_months=exp_data.get("duration_months"),
            )
            db.session.add(experience)

    def get_resume_details(self, resume_id: int) -> Dict:
        """Get detailed information about a resume."""
        resume = Resume.query.get(resume_id)
        if not resume:
            raise ValueError(f"Resume {resume_id} not found")

        return {
            "id": resume.id,
            "filename": resume.original_filename,
            "status": resume.status.value,
            "first_name": resume.owner.first_name,
            "last_name": resume.owner.last_name,
            "email": resume.owner.email,
            "skills": [
                {
                    "name": rs.skill.canonical_name,
                    "confidence": rs.confidence,
                    "category": rs.skill.category,
                }
                for rs in resume.skills
            ],
            "educations": [
                {
                    "institution": edu.institution,
                    "degree": edu.degree,
                    "field_of_study": edu.field_of_study,
                }
                for edu in resume.educations
            ],
            "experiences": [
                {
                    "company": exp.company,
                    "title": exp.title,
                    "duration_months": exp.duration_months,
                }
                for exp in resume.experiences
            ],
            "created_at": resume.created_at.isoformat() if resume.created_at else None,
        }
