import os
from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User
from models.job_role import JobRole, JobRoleSkill
from models.skill import Skill
from models.question import Question
from services.skill_extractor import DEFAULT_SKILL_TAXONOMY

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.resume import resume_bp
    from routes.interview import interview_bp
    from routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(profile_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error_code=404, error_title="Page Not Found", error_message="The requested URL was not found on this server."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', error_code=500, error_title="Internal Server Error", error_message="An internal server error occurred."), 500

    # Database Initialization & Automatic Seeding
    with app.app_context():
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
        db.create_all()
        migrate_db_schema()
        seed_initial_data()

    return app

def migrate_db_schema():
    """Safely add missing structured_json and completeness_score columns to resumes table."""
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE resumes ADD COLUMN structured_json TEXT;"))
                conn.commit()
            except Exception:
                pass
            try:
                conn.execute(text("ALTER TABLE resumes ADD COLUMN completeness_score FLOAT DEFAULT 0.0;"))
                conn.commit()
            except Exception:
                pass
    except Exception:
        pass

def seed_initial_data():
    """Seed initial master skills, job roles, role-skill mappings, and baseline question bank."""
    # 1. Seed Skills
    skill_objs = {}
    for cat, skills in DEFAULT_SKILL_TAXONOMY.items():
        for skill_name in skills:
            s = Skill.query.filter_by(name=skill_name).first()
            if not s:
                s = Skill(name=skill_name, category=cat)
                db.session.add(s)
                db.session.flush()
            skill_objs[skill_name] = s

    # 2. Seed Job Roles & Required Skills
    roles_data = [
        ("Python Developer", "Specializes in Python, web frameworks, backend APIs, and database engineering.", ["Python", "Flask", "Django", "SQL", "Git", "Docker"]),
        ("Data Scientist", "Leverages statistical modeling, machine learning, and data analysis to extract insights.", ["Python", "Pandas", "NumPy", "Scikit-learn", "Machine Learning", "SQL"]),
        ("Data Analyst", "Analyzes structured datasets, designs dashboards, and communicates business intelligence.", ["SQL", "Power BI", "Tableau", "Pandas", "Python"]),
        ("Machine Learning Engineer", "Deploys machine learning algorithms, deep learning models, and pipeline automation.", ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Docker"]),
        ("AI Engineer", "Develops LLM applications, RAG pipelines, prompt engineering, and generative AI systems.", ["Python", "Generative AI", "LLM", "RAG", "Prompt Engineering", "PyTorch"]),
        ("Full Stack Developer", "Builds end-to-end web applications across frontend UI and backend infrastructure.", ["JavaScript", "React", "Node.js", "Python", "SQL", "HTML", "CSS"]),
        ("Backend Developer", "Designs scalable server architecture, database schemas, and microservice APIs.", ["Python", "Flask", "SQL", "PostgreSQL", "Docker", "Git", "AWS"]),
        ("Software Engineer", "Engineers robust software applications following OOP principles and CI/CD pipelines.", ["Python", "C++", "Java", "SQL", "Git", "Docker"])
    ]

    for title, desc, req_skills in roles_data:
        role = JobRole.query.filter_by(title=title).first()
        if not role:
            role = JobRole(title=title, description=desc)
            db.session.add(role)
            db.session.flush()

            for sk in req_skills:
                s_obj = skill_objs.get(sk) or Skill.query.filter_by(name=sk).first()
                if s_obj:
                    jrs = JobRoleSkill(job_role_id=role.id, skill_id=s_obj.id, is_required=True)
                    db.session.add(jrs)

    # 3. Seed Sample Question Bank
    if Question.query.count() == 0:
        questions_seed = [
            ("Explain Python's memory management, garbage collection, and reference counting.", "Technical", "Medium", "Python"),
            ("How do RESTful API architecture principles differ from GraphQL design?", "Technical", "Medium", "Flask"),
            ("What strategies do you employ to handle overfitting in Machine Learning models?", "Technical", "Hard", "Machine Learning"),
            ("Describe the architectural pipeline of a Retrieval-Augmented Generation (RAG) system.", "Technical", "Hard", "LLM"),
            ("Describe a situation where you had a disagreement with a technical decision and how you resolved it.", "Behavioral", "Medium", None),
            ("How do you write efficient SQL queries and utilize database indexes?", "Technical", "Medium", "SQL"),
            ("Walk me through how Docker containers optimize deployment environments.", "Technical", "Easy", "Docker"),
            ("Explain how React handles state updates with the virtual DOM.", "Technical", "Medium", "React")
        ]

        for text, cat, diff, target_sk in questions_seed:
            target_sk_obj = skill_objs.get(target_sk) if target_sk else None
            q = Question(
                text=text,
                category=cat,
                difficulty=diff,
                target_skill_id=target_sk_obj.id if target_sk_obj else None,
                sample_answer="Thorough technical explanation detailing key concepts, practical trade-offs, and examples."
            )
            db.session.add(q)

    db.session.commit()

app = create_app()

if __name__ == '__main__':
    print("Starting Personalized Interview Preparation System (InterviewPrepAI)...")
    print("Application URL: http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
