import os
from app import create_app

config_name = os.environ.get("FLASK_CONFIG", "development")
app = create_app(config_name)

if __name__ == "__main__":
    with app.app_context():
        # Create tables
        from app.extensions import db
        db.create_all()

        # Create uploads directory
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    app.run(debug=True, host="0.0.0.0", port=5000)
