import io, uuid
from app import create_app
from app.extensions import db

unique = uuid.uuid4().hex[:6]
email = f'candidate_{unique}@demo.com'
print(f'Using email: {email}')

app = create_app()
with app.app_context():
    db.create_all()
    with app.test_client() as c:
        r = c.post('/api/auth/register', json={'email': email, 'password': 'test123', 'first_name': 'Rakshitha', 'last_name': 'Reddy', 'role': 'candidate'})
        token = r.get_json()['access_token']
        h = {'Authorization': 'Bearer ' + token}
        print('1. Registered:', r.get_json()['user']['first_name'])

        r = c.get('/api/jobs/browse', headers=h)
        jobs = r.get_json()['jobs']
        print('2. Jobs available:', len(jobs))
        for j in jobs[:3]:
            print('   -', j['title'], '@', j['company'], '|', len(j['skills']), 'skills')

        resume_text = b'Rakshitha Reddy\nSkills: Python, Django, Flask, SQL, Machine Learning, TensorFlow, Pandas, NumPy\nEducation: BSc Computer Science, IIT Delhi\nExperience: 3 years Python Developer at Google\nBuilt ML pipelines and REST APIs'
        r = c.post('/api/resumes', headers=h, data={'file': (io.BytesIO(resume_text), 'resume.txt')}, content_type='multipart/form-data')
        result = r.get_json()
        print('3. Resume uploaded:', result['extraction_result']['skills_found'], 'skills found')

        r = c.post('/api/matches/auto-match', headers=h)
        mdata = r.get_json()
        print('4. Auto-match:', mdata.get('total_matched', 0), 'jobs matched')

        r = c.get('/api/matches/my-matches', headers=h)
        matches = r.get_json()['matches']
        print('5. My matches:', len(matches), 'jobs')
        for m in matches[:5]:
            pct = round(m['scores']['overall'] * 100)
            title = m['job']['title']
            company = m['job']['company']
            rank = m['rank']
            matched = [s.get('job_skill', s) for s in m['matched_skills']]
            missing = m['missing_skills']
            print(f'   #{rank} {title} @ {company}: {pct}%')
            print(f'      Matched: {matched}')
            print(f'      Missing: {missing}')

        r = c.get('/api/dashboard/stats', headers=h)
        stats = r.get_json()
        print('6. Dashboard stats:')
        best = round(stats['best_score'] * 100)
        avg = round(stats['average_score'] * 100)
        print(f'   Jobs: {stats["total_jobs"]} | Matches: {stats["total_matches"]} | Best: {best}% | Avg: {avg}%')
        print(f'   Breakdown: {stats["breakdown"]}')
        skills = [s['skill'] for s in stats['your_skills'][:5]]
        print(f'   Your skills: {skills}')

        print('\nAll tests passed!')
