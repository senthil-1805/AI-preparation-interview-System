from models import db

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Technical')  # Technical, Behavioral, HR, Scenario-based
    difficulty = db.Column(db.String(20), nullable=False, default='Medium')    # Easy, Medium, Hard
    job_role_id = db.Column(db.Integer, db.ForeignKey('job_roles.id'), nullable=True)
    target_skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=True)
    sample_answer = db.Column(db.Text, nullable=True)

    job_role = db.relationship('JobRole', backref='questions')
    target_skill = db.relationship('Skill', backref='questions')

    def __repr__(self):
        return f'<Question {self.id}: {self.category} ({self.difficulty})>'
