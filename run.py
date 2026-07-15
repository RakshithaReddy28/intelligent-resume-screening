from app import create_app
from seed_jobs import seed_jobs

app = create_app()

with app.app_context():
    seed_jobs()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
