# Intelligent Resume Screening System

A professional resume screening system built with Flask, PostgreSQL, NLP, and ML.

## Features

- **Resume Upload & Parsing**: Support for PDF, DOCX, and TXT formats
- **NLP Extraction**: Extract skills, education, and experience from resumes
- **Intelligent Matching**: Match resumes against job descriptions using ML
- **Multi-Signal Scoring**: Skills (40%), Experience (30%), Education (10%), Semantic (20%)
- **Candidate Ranking**: Rank candidates by match score
- **Dashboard**: Analytics and recent activity for recruiters

## Tech Stack

- **Backend**: Flask + SQLAlchemy + PostgreSQL
- **NLP**: spaCy + Custom extractors
- **ML**: scikit-learn (TF-IDF + Cosine Similarity)
- **Auth**: JWT Authentication
- **Frontend**: Bootstrap + Jinja2 Templates

## Project Structure

```
intelligent_resume_screening/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration
│   ├── extensions.py        # Flask extensions
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # Flask Blueprints
│   ├── services/            # Business logic
│   ├── parsers/             # Resume file parsing
│   ├── extractors/          # NLP extraction
│   ├── ml/                  # ML matching
│   └── templates/           # Jinja2 templates
├── data/                    # Skill taxonomy
├── uploads/                 # Resume storage
├── requirements.txt
└── run.py
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- PostgreSQL
- pip

### 2. Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb resume_screening_dev

# Set environment variable
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resume_screening_dev

# Initialize database
python -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 4. Configuration

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

### 5. Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Resumes
- `POST /api/resumes` - Upload resume
- `GET /api/resumes` - List resumes
- `GET /api/resumes/<id>` - Get resume details
- `DELETE /api/resumes/<id>` - Delete resume

### Jobs
- `POST /api/jobs` - Create job (recruiter only)
- `GET /api/jobs` - List jobs
- `GET /api/jobs/<id>` - Get job details
- `PUT /api/jobs/<id>` - Update job
- `DELETE /api/jobs/<id>` - Delete job

### Matching
- `POST /api/matches/job/<job_id>` - Run matching
- `GET /api/matches/job/<job_id>` - Get match results
- `GET /api/matches/<match_id>` - Get match details

### Dashboard
- `GET /api/dashboard/stats` - Get statistics
- `GET /api/dashboard/recent-activity` - Get recent activity

## Matching Algorithm

The system uses a multi-signal scoring approach:

1. **Skill Matching (40%)**: Exact and fuzzy matching of skills
2. **Experience Matching (30%)**: Years of experience comparison
3. **Education Matching (10%)**: Degree level comparison
4. **Semantic Similarity (20%)**: TF-IDF + Cosine similarity

## License

MIT License
