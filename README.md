# Job Match Finder

An intelligent job matching platform that helps candidates discover how well they match with available jobs. Upload your resume and instantly see match scores across all positions.

## Features

- **Resume Upload & Parsing**: Support for PDF, DOCX, and TXT formats
- **NLP Extraction**: Automatically extract skills, education, and experience
- **Smart Matching**: Multi-signal scoring against job descriptions
- **Instant Auto-Match**: Match your resume against all jobs in one click
- **Match Scores**: See percentage match with breakdown (Skills, Experience, Education, Semantic)
- **Skill Gap Analysis**: View matched vs missing skills for each job
- **Job Role Classification**: AI classifies your resume into best-fit job roles
- **Search & Filter**: Search jobs by title, company, skills, or location
- **Dashboard**: Stats, score breakdown, recent matches, top skills

## Tech Stack

- **Backend**: Flask + SQLAlchemy + MySQL
- **NLP**: spaCy + Custom extractors
- **ML**: scikit-learn (TF-IDF + Cosine Similarity) + RapidFuzz (fuzzy matching)
- **Auth**: JWT Authentication
- **Frontend**: Bootstrap 5 + Vanilla JS

## Matching Algorithm

Multi-signal scoring approach:

| Signal | Weight | How it works |
|--------|--------|-------------|
| Skills | 40% | Exact + fuzzy matching of required skills |
| Experience | 30% | Years of experience comparison |
| Education | 10% | Degree level comparison |
| Semantic | 20% | TF-IDF cosine similarity of resume vs job description |

## Setup

### Prerequisites
- Python 3.9+
- MySQL

### Installation
```bash
# Clone the repo
git clone https://github.com/RakshithaReddy28/intelligent-resume-screening.git
cd intelligent-resume-screening

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Database Setup
```bash
# Create MySQL database
mysql -u root -p -e "CREATE DATABASE resume_screening_dev;"

# Update config.py with your MySQL credentials, then:
python seed_jobs.py    # Seeds 10 sample jobs

# Run the app
python run.py
```

Visit **http://127.0.0.1:5000**

## How It Works

1. **Register** as a candidate
2. **Upload your resume** (PDF/DOCX/TXT)
3. System **extracts** your skills, education, and experience
4. Click **Auto-Match** to match against all 10 jobs instantly
5. **Browse Jobs** to see match %, matched skills, and missing skills
6. **View Dashboard** for stats and score breakdown

## Project Structure

```
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # MySQL configuration
│   ├── extensions.py        # Flask extensions
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # API + page routes
│   ├── services/            # Business logic
│   ├── parsers/             # Resume file parsing (PDF/DOCX/TXT)
│   ├── extractors/          # NLP entity extraction
│   ├── ml/                  # ML matching + classification
│   └── templates/           # Frontend templates
├── data/
│   └── skills_taxonomy.json # Skill database
├── requirements.txt
├── seed_jobs.py             # Sample job seeder
└── run.py                   # Entry point
```

## License

MIT License
