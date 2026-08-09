# Personalized Interview Preparation System (InterviewPrepAI)

An AI-powered, full-stack web application built with **Python & Flask** that empowers candidates to prepare smarter and interview better. The platform extracts structured technical and professional information from PDF resumes, performs target role skill-gap analysis, generates dynamic personalized interview questions tailored to candidate projects and experiences, evaluates responses using AI or a deterministic fallback engine, and delivers comprehensive performance reports.

---

## 🌟 Key Features

1. **User Authentication & Profiles**: Secure registration, password hashing (`Werkzeug`), session management (`Flask-Login`), and target job role configuration.
2. **Structured PDF Resume Parsing**: Multi-page PDF extraction via `pdfplumber` with section detection and regex extraction of:
   - **Personal Information**: Full Name, Email, Phone, Address, LinkedIn, GitHub, Portfolio.
   - **Professional Summary**: Profile statement & career objective.
   - **Categorized Skill Taxonomy**: Technical, Programming Languages, Frameworks, Databases, Cloud, DevOps, AI/ML, Soft Skills.
   - **Structured Section Records**: Work Experience (Company, Title, Dates, Responsibilities), Education (Degree, Institution, Dates, GPA), Projects (Name, Tech Stack, Description, URL), Certifications, Spoken Languages, and Achievements.
3. **Resume Quality Index & Analysis UI**: Calculates a 0-100% completeness score across 9 core resume categories, highlights missing sections, and displays structured profile dashboards instead of raw text dumps.
4. **Role-Based Skill Gap Analysis**: Compares candidate skills against required skills for 8 target job roles (Python Developer, Data Scientist, ML Engineer, AI Engineer, Full Stack, Backend, Frontend, Data Analyst) and computes a visual coverage percentage.
5. **Project & Experience Tailored Question Generator**: Synthesizes custom interview questions specifically referencing the candidate's resume projects and previous company experiences, alongside standard role-based technical questions.
6. **Dual AI / Fallback Evaluation Engine**:
   - **API Mode**: Integrates with OpenAI / Gemini LLM APIs when keys are configured.
   - **DEMO Mode**: Deterministic fallback engine using `scikit-learn` TF-IDF cosine similarity, keyword coverage, and length heuristics when running standalone without API keys.
7. **Executive Visual Dashboard**: Interactive Chart.js graphs displaying interview score trends, skill coverage doughnuts, recent interview history, resume completeness statistics, and targeted study recommendations.
8. **Comprehensive Performance Reports**: Detailed breakdown of Technical, Communication, and Relevance scores, key strengths, growth opportunities, and recommended topics.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12+, Flask, Flask-SQLAlchemy, Flask-Login, Werkzeug, SQLite
- **Frontend**: HTML5, CSS3 (Custom Glassmorphism Design System), JavaScript, Bootstrap 5, Jinja2, Chart.js
- **Resume Processing**: `pdfplumber`, regular expression (regex) section parsing
- **NLP & AI**: `scikit-learn` (TF-IDF vectorizer & cosine similarity), REST API abstractions for OpenAI / Gemini LLMs

---

## 📁 Project Structure
InterviewPrepAI/ │ ├── app.py # Flask Application Entry Point, DB Seeder & Schema Migration ├── config.py # App Configuration & Environment Variables ├── requirements.txt # Python Package Dependencies ├── .env # Local Environment Variables ├── .env.example # Example Environment Template ├── .gitignore # Git Ignore Rules ├── README.md # Documentation │ ├── instance/ │ └── interview_prep.db # SQLite Database File │ ├── models/ # SQLAlchemy Database Models │ ├── init.py │ ├── user.py # User Account & Password Hashing │ ├── resume.py # Resume Metadata & Structured JSON Data │ ├── skill.py # Master Skills & User Skill Mappings │ ├── job_role.py # Job Roles & Required Role Skills │ ├── interview.py # Interview Sessions │ ├── question.py # Question Bank │ ├── answer.py # User Responses & Evaluation Scores │ ├── score.py # Aggregate Scores & Feedback │ └── recommendation.py # Recommendations & Progress History │ ├── routes/ # Flask Blueprints │ ├── init.py │ ├── auth.py # Auth Routes (Login, Register, Logout) │ ├── dashboard.py # Dashboard & Analytics Routes │ ├── resume.py # Resume Upload, Analysis & Skill Gap Routes │ ├── interview.py # Mock Interview & Report Routes │ └── profile.py # Profile & Target Role Routes │ ├── services/ # Application Services & Business Logic │ ├── init.py │ ├── resume_parser.py # PDF Multi-Page Extraction & Section Parser │ ├── skill_extractor.py # Skill Taxonomy Engine │ ├── skill_gap.py # Skill Gap Matrix Analyzer │ ├── question_generator.py # Tailored Question Generator (Projects & Experiences) │ ├── ai_service.py # Unified AI Service Abstraction │ ├── ai_evaluator.py # AI Answer Evaluator Wrapper │ ├── fallback_evaluator.py # Deterministic DEMO Fallback Evaluator │ └── recommendation_engine.py# Study Recommendation Generator │ ├── utils/ # Helper Functions & Validators │ ├── init.py │ ├── validators.py # Form & File Input Validation │ └── helpers.py # Security & Utility Functions │ ├── templates/ # Jinja2 HTML Templates │ ├── base.html │ ├── index.html │ ├── login.html │ ├── register.html │ ├── dashboard.html │ ├── upload_resume.html │ ├── resume_analysis.html # Structured Resume Analysis Dashboard │ ├── skills.html │ ├── skill_gap.html │ ├── start_interview.html │ ├── interview.html │ ├── report.html │ ├── profile.html │ └── error.html │ ├── static/ # Static Assets │ ├── css/ │ │ └── style.css # Glassmorphism Modern UI CSS │ └── js/ │ └── app.js # Client JavaScript │ ├── uploads/ # Secure PDF Resume Upload Directory │ └── tests/ # Automated Unit Test Suite ├── init.py ├── test_auth.py ├── test_resume.py └── test_interview.py
