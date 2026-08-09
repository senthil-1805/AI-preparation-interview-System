import json
from datetime import datetime, timezone
from models import db

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    raw_text = db.Column(db.Text, nullable=True)
    parsed_name = db.Column(db.String(120), nullable=True)
    parsed_email = db.Column(db.String(120), nullable=True)
    parsed_phone = db.Column(db.String(50), nullable=True)
    parsed_education = db.Column(db.Text, nullable=True)
    parsed_experience = db.Column(db.Text, nullable=True)
    parsed_projects = db.Column(db.Text, nullable=True)
    parsed_certifications = db.Column(db.Text, nullable=True)
    structured_json = db.Column(db.Text, nullable=True)
    completeness_score = db.Column(db.Float, default=0.0)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def get_structured_data(self):
        """Returns deserialized structured JSON dictionary or default template."""
        if self.structured_json:
            try:
                return json.loads(self.structured_json)
            except Exception:
                pass
        return {
            "personal_information": {
                "name": self.parsed_name or "",
                "email": self.parsed_email or "",
                "phone": self.parsed_phone or "",
                "address": "",
                "linkedin": "",
                "github": "",
                "portfolio": ""
            },
            "profile": "",
            "skills": {
                "technical": [],
                "programming_languages": [],
                "frameworks": [],
                "databases": [],
                "cloud": [],
                "tools": [],
                "ai_ml": [],
                "soft_skills": [],
                "other": []
            },
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "languages": [],
            "achievements": [],
            "completeness_score": self.completeness_score or 0.0,
            "missing_sections": []
        }

    def __repr__(self):
        return f'<Resume {self.filename} for User {self.user_id}>'
