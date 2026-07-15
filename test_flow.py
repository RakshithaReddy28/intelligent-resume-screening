import io, json
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    db.create_all()
    with app.test_client() as c:
        # Setup
        r = c.post('/api/auth/register', json={'email': 'rec6@demo.com', 'password': 'test123', 'first_name': 'Rec', 'last_name': 'Ruiter', 'role': 'recruiter'})
        rh = {'Authorization': 'Bearer ' + r.get_json()['access_token']}

        r = c.post('/api/auth/register', json={'email': 'can6@demo.com', 'password': 'test123', 'first_name': 'John', 'last_name': 'Doe', 'role': 'candidate'})
        ch = {'Authorization': 'Bearer ' + r.get_json()['access_token']}

        # Create jobs
        j1 = c.post('/api/jobs', headers=rh, json={'title': 'Python Developer', 'company': 'TechCorp', 'description': 'Python Django Flask SQL REST APIs', 'skills': [{'name': 'Python', 'is_required': True}, {'name': 'Django', 'is_required': True}]}).get_json()['job_id']
        j2 = c.post('/api/jobs', headers=rh, json={'title': 'Data Scientist', 'company': 'DataInc', 'description': 'ML TensorFlow PyTorch deep learning', 'skills': [{'name': 'Python', 'is_required': True}, {'name': 'Machine Learning', 'is_required': True}]}).get_json()['job_id']
        print('=== JOBS CREATED ===')

        # Upload resumes
        resume1 = b'John Doe\nSkills: Python, Django, Flask, SQL, Machine Learning, TensorFlow\nEducation: BSc Computer Science\nExperience: 3 years Python Developer at Google'
        resume2 = b'Jane Smith\nSkills: JavaScript, React, HTML, CSS, Node.js\nEducation: BSc Software Engineering\nExperience: 2 years Frontend Developer at Meta'
        r = c.post('/api/resumes', headers=ch, data={'file': (io.BytesIO(resume1), 'john.txt')}, content_type='multipart/form-data')
        print('Resume 1:', r.get_json()['extraction_result']['skills_found'], 'skills')
        r = c.post('/api/resumes', headers=ch, data={'file': (io.BytesIO(resume2), 'jane.txt')}, content_type='multipart/form-data')
        print('Resume 2:', r.get_json()['extraction_result']['skills_found'], 'skills')

        # Run matching
        c.post(f'/api/matches/job/{j1}', headers=rh)
        c.post(f'/api/matches/job/{j2}', headers=rh)
        print('\n=== MATCHING COMPLETED ===')

        # 1. Ranked results
        r = c.get(f'/api/matches/job/{j1}', headers=rh)
        results = r.get_json()['results']
        print(f'\n--- Ranked Candidates for Python Developer ({len(results)} total) ---')
        for res in results:
            print(f"  #{res['rank']} {res['candidate']['name']}: {round(res['scores']['overall']*100)}%")

        # 2. Shortlisting
        r = c.get(f'/api/matches/job/{j1}/shortlist', headers=rh)
        data = r.get_json()
        stats = data['stats']
        print(f'\n--- Shortlisting Recommendations ---')
        print(f"  Auto-Shortlist (>=75%): {stats['auto_shortlist_count']}")
        print(f"  Recommended (55-75%):   {stats['recommended_count']}")
        print(f"  Borderline (40-55%):    {stats['borderline_count']}")
        print(f"  Not Recommended (<40%): {stats['not_recommended_count']}")
        for cat, entries in data['categories'].items():
            for e in entries:
                print(f"    [{cat}] {e['candidate_name']}: {round(e['overall_score']*100)}% - {e['recommendation']}")

        # 3. Skill Gap Analysis
        r = c.get(f'/api/matches/job/{j1}/skill-gap', headers=rh)
        gap = r.get_json()
        print(f'\n--- Skill Gap Analysis (Job: Python Developer) ---')
        print(f"  Total candidates: {gap['total_candidates']}")
        for s in gap['skill_coverage']:
            print(f"  Coverage: {s['skill']} = {s['coverage']}%")
        for s in gap['skill_gaps']:
            print(f"  Gap: {s['skill']} = {s['gap_percentage']}% missing")

        # 4. Resume Classification
        resume_id = c.get('/api/resumes', headers=ch).get_json()['resumes'][0]['id']
        r = c.get(f'/api/matches/classify/{resume_id}', headers=rh)
        cls = r.get_json()
        print(f'\n--- Resume Classification for {cls["filename"]} ---')
        for c_item in cls['classifications']:
            print(f"  {c_item['role']}: {round(c_item['confidence']*100)}% (matched: {c_item['matched_skills']})")

        # 5. Dashboard stats
        r = c.get('/api/dashboard/stats', headers=rh)
        stats = r.get_json()
        print(f'\n--- Dashboard Stats ---')
        print(f"  Jobs: {stats.get('total_jobs', 0)} | Matches: {stats.get('total_matches', 0)} | Shortlisted: {stats.get('shortlisted_count', 0)} | Avg: {round(stats.get('average_match_score', 0)*100)}%")

        # 6. Job summary
        r = c.get(f'/api/dashboard/job/{j1}/summary', headers=rh)
        summary = r.get_json()
        funnel = summary['funnel']
        print(f'\n--- Job Summary: {summary["job"]["title"]} ---')
        print(f"  Evaluated: {funnel['total_evaluated']} | Shortlisted: {funnel['shortlisted']} | Good: {funnel['good']} | Borderline: {funnel['borderline']} | Rejected: {funnel['rejected']}")
