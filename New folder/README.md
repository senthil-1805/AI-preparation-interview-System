# Personalized Interview Preparation System (InterviewPrepAI)

An AI-powered, full-stack web application built with **Python & Flask** that empowers candidates to prepare smarter and interview better. The platform extracts technical skills from PDF resumes, performs target role skill-gap analysis, generates dynamic personalized interview questions, evaluates responses using AI or a deterministic fallback engine, and delivers comprehensive performance reports.

---

## 🌟 Key Features

1. **User Authentication & Profiles**: Secure registration, password hashing (`Werkzeug`), session management (`Flask-Login`), and target job role configuration.
2. **PDF Resume Parsing**: Automated text extraction via `pdfplumber` with regex extraction of candidate contact info, education, experience, projects, and certifications.
3. **Skill Taxonomy & Extraction**: Matches resume text against a configurable 35+ technology skill taxonomy (Python, Java, React, SQL, Docker, AWS, LLM, RAG, etc.).
4. **Role-Based Skill Gap Analysis**: Compares candidate skills against required skills for 8 target job roles (Python Dev, Data Scientist, ML Engineer, AI Engineer, Full Stack, Backend, Frontend, Data Analyst) and computes a visual coverage percentage.
5. **Dynamic Mock Interview Generator**: Assembles multi-category interview questions (Technical, Behavioral, HR, Scenario-based) tailored to the candidate's target role and missing skills.
6. **Dual AI / Fallback Evaluation Engine**:
   - **API Mode**: Integrates with OpenAI / Gemini APIs when keys are configured.
   - **DEMO Mode**: Deterministic fallback engine using TF-IDF cosine similarity, keyword coverage, and length heuristics when running without API keys.
7. **Executive Visual Dashboard**: Interactive Chart.js graphs displaying interview score trends, skill coverage dough-nuts, recent interview history, and targeted study recommendations.
8. **Comprehensive Performance Reports**: Detailed breakdown of Technical, Communication, and Relevance scores, key strengths, growth opportunities, and recommended topics.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12+, Flask, Flask-SQLAlchemy, Flask-Login, Werkzeug, SQLite
- **Frontend**: HTML5, CSS3 (Custom Glassmorphism), JavaScript, Bootstrap 5, Jinja2, Chart.js
- **Resume Processing**: `pdfplumber`, regex text parsing
- **NLP & AI**: `scikit-learn` (TF-IDF vectorizer & cosine similarity), REST API abstractions for OpenAI / Gemini LLMs

---

## 📁 Project Structure

```
InterviewPrepAI/
│
├── app.py                      # Flask Application Entry Point & DB Seeder
├── config.py                   # App Configuration & Environment Variables
├── requirements.txt            # Python Package Dependencies
├── .env                        # Local Environment Variables
├── .env.example                # Example Environment Template
├── .gitignore                  # Git Ignore Rules
├── README.md                   # Documentation
│
├── instance/
│   └── interview_prep.db       # SQLite Database File
│
├── models/                     # SQLAlchemy Database Models
│   ├── __init__.py
│   ├── user.py                 # User Account & Password Hashing
│   ├── resume.py               # Resume Metadata & Extracted Text
│   ├── skill.py                # Master Skills & User Skill Mappings
│   ├── job_role.py             # Job Roles & Required Role Skills
│   ├── interview.py            # Interview Sessions
│   ├── question.py             # Question Bank
│   ├── answer.py               # User Responses & Evaluation Scores
│   ├── score.py                # Aggregate Scores & Feedback
│   └── recommendation.py       # Recommendations & Progress History
│
├── routes/                     # Flask Blueprints
│   ├── __init__.py
│   ├── auth.py                 # Auth Routes (Login, Register, Logout)
│   ├── dashboard.py            # Dashboard & Analytics Routes
│   ├── resume.py               # Resume Upload & Skill Gap Routes
│   ├── interview.py            # Mock Interview & Report Routes
│   └── profile.py              # Profile & Target Role Routes
│
├── services/                   # Application Services & Business Logic
│   ├── __init__.py
│   ├── resume_parser.py        # PDF Extraction & Text Parser
│   ├── skill_extractor.py      # Skill Taxonomy Engine
│   ├── skill_gap.py            # Skill Gap Matrix Analyzer
│   ├── question_generator.py   # Tailored Question Generator
│   ├── ai_service.py           # Unified AI Service Abstraction
│   ├── ai_evaluator.py         # AI Answer Evaluator Wrapper
│   ├── fallback_evaluator.py   # Deterministic DEMO Fallback Evaluator
│   └── recommendation_engine.py# Study Recommendation Generator
│
├── utils/                      # Helper Functions & Validators
│   ├── __init__.py
│   ├── validators.py           # Form & File Input Validation
│   └── helpers.py              # Security & Utility Functions
│
├── templates/                  # Jinja2 HTML Templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── upload_resume.html
│   ├── skills.html
│   ├── skill_gap.html
│   ├── start_interview.html
│   ├── interview.html
│   ├── report.html
│   ├── profile.html
│   └── error.html
│
├── static/                     # Static Assets
│   ├── css/
│   │   └── style.css           # Glassmorphism Modern UI CSS
│   └── js/
│       └── app.js              # Client JavaScript
│
├── uploads/                    # Secure PDF Resume Upload Directory
│
└── tests/                      # Automated Unit Test Suite
    ├── __init__.py
    ├── test_auth.py
    ├── test_resume.py
    └── test_interview.py
```

---

## ⚡ Quick Start & Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd InterviewPrepAI
   ```

2. **Install Python dependencies**:
   ```bash
   python -m pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   AI_MODE=demo
   SECRET_KEY=interview-prep-ai-super-secret-key-2026
   ```

4. **Run Automated Unit Tests**:
   ```bash
   python -m unittest discover tests
   ```

5. **Start Flask Server**:
   ```bash
   python app.py
   ```

6. **Access in Web Browser**:
   Navigate to `http://127.0.0.1:5000`

---

## 🤖 Dual AI Mode vs Demo Mode

- **Demo Mode (`AI_MODE=demo`)**: Activated by default when no API key is specified. The system utilizes `scikit-learn` TF-IDF vectorization, keyword matching, and length heuristics to score candidate answers deterministically on a 0-100 scale.
- **API Mode (`AI_MODE=api`)**: When an `OPENAI_API_KEY` or `GEMINI_API_KEY` is present in `.env`, the application automatically uses LLM API calls to evaluate responses with natural language feedback.

---

## 🚀 Future Enhancements

- Audio voice answer recording & speech-to-text translation.
- Adaptive difficulty scaling during live mock interviews.
- Export interview performance report as a downloadable PDF certificate.
