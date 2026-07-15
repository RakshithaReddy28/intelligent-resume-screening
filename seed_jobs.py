"""Seed script - creates sample jobs in the database."""
from app import create_app
from app.extensions import db
from app.models.job import Job, JobSkill
from app.models.skill import Skill
from app.models.enums import JobStatus

SAMPLE_JOBS = [
    {
        "title": "Python Full Stack Developer",
        "company": "TechNova Solutions",
        "description": "Looking for a Python full stack developer with experience in Django/Flask, REST APIs, PostgreSQL, and front-end basics. Must have 2+ years experience with Python and web frameworks.",
        "location": "Bangalore, India",
        "job_type": "full-time",
        "experience_min_years": 2,
        "experience_max_years": 5,
        "education_level": "bachelors",
        "skills": ["Python", "Django", "Flask", "SQL", "REST API", "HTML", "CSS", "JavaScript"],
    },
    {
        "title": "Data Scientist",
        "company": "Insight Analytics",
        "description": "Data scientist role requiring expertise in machine learning, deep learning, Python, and statistical modeling. Experience with TensorFlow or PyTorch preferred. Must have strong analytical skills.",
        "location": "Hyderabad, India",
        "job_type": "full-time",
        "experience_min_years": 1,
        "experience_max_years": 4,
        "education_level": "masters",
        "skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "SQL", "Pandas", "NumPy"],
    },
    {
        "title": "Frontend Web Developer",
        "company": "Creative Digital Agency",
        "description": "We need a frontend developer skilled in React.js, JavaScript, HTML5, CSS3. Experience with responsive design, Bootstrap, and modern UI/UX practices.",
        "location": "Mumbai, India",
        "job_type": "full-time",
        "experience_min_years": 1,
        "experience_max_years": 3,
        "education_level": "bachelors",
        "skills": ["JavaScript", "React", "HTML", "CSS", "Bootstrap", "TypeScript", "Angular"],
    },
    {
        "title": "DevOps Engineer",
        "company": "CloudFirst Inc",
        "description": "DevOps engineer with expertise in AWS/Azure, Docker, Kubernetes, CI/CD pipelines, Terraform. Linux administration and scripting required.",
        "location": "Pune, India",
        "job_type": "full-time",
        "experience_min_years": 2,
        "experience_max_years": 6,
        "education_level": "bachelors",
        "skills": ["AWS", "Docker", "Kubernetes", "Linux", "Terraform", "Jenkins", "CI/CD", "Python"],
    },
    {
        "title": "Machine Learning Engineer",
        "company": "AI Dynamics",
        "description": "ML Engineer to build and deploy machine learning models at scale. Experience with NLP, computer vision, MLOps. Python, TensorFlow, PyTorch, and cloud deployment.",
        "location": "Bangalore, India",
        "job_type": "full-time",
        "experience_min_years": 2,
        "experience_max_years": 5,
        "education_level": "masters",
        "skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP", "Docker", "AWS"],
    },
    {
        "title": "Java Backend Developer",
        "company": "FinServe Technologies",
        "description": "Backend developer with strong Java, Spring Boot, Microservices experience. SQL databases, REST APIs, and messaging queues like Kafka.",
        "location": "Chennai, India",
        "job_type": "full-time",
        "experience_min_years": 3,
        "experience_max_years": 7,
        "education_level": "bachelors",
        "skills": ["Java", "Spring Boot", "SQL", "REST API", "Microservices", "Kafka", "Redis"],
    },
    {
        "title": "Data Analyst",
        "company": "MarketEdge Analytics",
        "description": "Data analyst to analyze business data, create dashboards and reports. SQL, Excel, Python, Tableau/Power BI. Good communication skills required.",
        "location": "Delhi NCR, India",
        "job_type": "full-time",
        "experience_min_years": 0,
        "experience_max_years": 3,
        "education_level": "bachelors",
        "skills": ["SQL", "Python", "Excel", "Tableau", "Power BI", "Statistics", "Data Visualization"],
    },
    {
        "title": "Mobile App Developer",
        "company": "AppWorks Studio",
        "description": "Mobile developer for iOS and Android apps. Flutter or React Native experience preferred. Swift, Kotlin knowledge. REST API integration.",
        "location": "Remote",
        "job_type": "full-time",
        "experience_min_years": 1,
        "experience_max_years": 4,
        "education_level": "bachelors",
        "skills": ["Flutter", "React Native", "Swift", "Kotlin", "JavaScript", "REST API", "Firebase"],
    },
]


def seed_jobs():
    """Create sample jobs if none exist."""
    app = create_app()
    with app.app_context():
        existing = Job.query.count()
        if existing > 0:
            print(f"Database already has {existing} jobs. Skipping seed.")
            return

        for job_data in SAMPLE_JOBS:
            job = Job(
                recruiter_id=0,
                title=job_data["title"],
                company=job_data["company"],
                description=job_data["description"],
                location=job_data.get("location"),
                job_type=job_data.get("job_type", "full-time"),
                experience_min_years=job_data.get("experience_min_years"),
                experience_max_years=job_data.get("experience_max_years"),
                education_level=job_data.get("education_level"),
                status=JobStatus.ACTIVE,
            )
            db.session.add(job)
            db.session.flush()

            for skill_name in job_data["skills"]:
                skill = Skill.query.filter(
                    db.func.lower(Skill.canonical_name) == skill_name.lower()
                ).first()
                if not skill:
                    skill = Skill(name=skill_name, canonical_name=skill_name.lower(), category="general")
                    db.session.add(skill)
                    db.session.flush()

                job_skill = JobSkill(job_id=job.id, skill_id=skill.id, is_required=True)
                db.session.add(job_skill)

        db.session.commit()
        print(f"Seeded {len(SAMPLE_JOBS)} jobs successfully!")


if __name__ == "__main__":
    seed_jobs()
