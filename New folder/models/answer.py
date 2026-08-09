from datetime import datetime, timezone
from models import db

class Answer(db.Model):
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_answer = db.Column(db.Text, nullable=True)
    relevance_score = db.Column(db.Float, default=0.0)
    technical_score = db.Column(db.Float, default=0.0)
    completeness_score = db.Column(db.Float, default=0.0)
    clarity_score = db.Column(db.Float, default=0.0)
    overall_score = db.Column(db.Float, default=0.0)
    feedback = db.Column(db.Text, nullable=True)
    is_evaluated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    question = db.relationship('Question', backref='user_answers')

    def __repr__(self):
        return f'<Answer {self.id} for Interview {self.interview_id}>'
