from datetime import datetime, timezone
from models import db

class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='General')

    def __repr__(self):
        return f'<Skill {self.name}>'

class UserSkill(db.Model):
    __tablename__ = 'user_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    source = db.Column(db.String(50), default='resume')  # 'resume' or 'manual'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    skill = db.relationship('Skill', backref='user_mappings')
