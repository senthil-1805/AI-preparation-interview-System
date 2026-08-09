from datetime import datetime, timezone
from models import db

class JobRole(db.Model):
    __tablename__ = 'job_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    role_skills = db.relationship('JobRoleSkill', backref='job_role', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<JobRole {self.title}>'

class JobRoleSkill(db.Model):
    __tablename__ = 'job_role_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    job_role_id = db.Column(db.Integer, db.ForeignKey('job_roles.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    is_required = db.Column(db.Boolean, default=True)

    skill = db.relationship('Skill', backref='job_roles_mapped')
