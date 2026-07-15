from app.extensions import db


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    canonical_name = db.Column(db.String(100), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=True)  # programming, soft, domain
    synonyms = db.Column(db.JSON, nullable=True)  # ["js", "javascript"]
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Skill {self.name}>"
