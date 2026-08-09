from datetime import datetime, timezone
from models import db

class Interview(db.Model):
    __tablename__ = 'interviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_role_id = db.Column(db.Integer, db.ForeignKey('job_roles.id'), nullable=False)
    total_questions = db.Column(db.Integer, default=5)
    status = db.Column(db.String(20), default='in_progress')  # 'in_progress', 'completed'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    job_role = db.relationship('JobRole', backref='interviews')
    answers = db.relationship('Answer', backref='interview', cascade='all, delete-orphan')
    scores = db.relationship('InterviewScore', backref='interview', uselist=False, cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='interview', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Interview {self.id} for User {self.user_id} - Status: {self.status}>'
