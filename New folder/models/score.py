from datetime import datetime, timezone
from models import db

class InterviewScore(db.Model):
    __tablename__ = 'interview_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'), nullable=False)
    overall_score = db.Column(db.Float, nullable=False, default=0.0)
    technical_score = db.Column(db.Float, nullable=False, default=0.0)
    communication_score = db.Column(db.Float, nullable=False, default=0.0)
    relevance_score = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(50), default='Needs Practice')
    strengths = db.Column(db.Text, nullable=True)
    weak_areas = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<InterviewScore for Interview {self.interview_id}: {self.overall_score}%>'
