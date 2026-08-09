import random
from models.question import Question
from models.resume import Resume

class QuestionGenerator:
    @staticmethod
    def generate_questions_for_interview(user, job_role, count=5):
        """
        Generate personalized question set tailored to:
        - Candidate's extracted Projects from Resume
        - Work Experience & Companies from Resume
        - Extracted Resume Skills & Target Role Skill Gaps
        - Technical, Behavioral, HR, Scenario-based categories
        """
        # Fetch latest resume structured data
        latest_resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()
        structured = latest_resume.get_structured_data() if latest_resume else {}

        personalized_questions = []

        # 1. Generate Project-specific questions from Resume
        projects = structured.get("projects", [])
        for proj in projects[:2]:
            proj_name = proj.get("name")
            if proj_name and len(proj_name) > 3:
                techs = ", ".join(proj.get("technologies", [])) if proj.get("technologies") else "modern software stack"
                q = Question(
                    text=f"In your resume project '{proj_name}', walk us through the system architecture, why you chose {techs}, and how you handled key implementation challenges.",
                    category="Technical",
                    difficulty="Medium",
                    sample_answer=f"Explain high-level design patterns, data flow, and trade-offs made while building {proj_name}."
                )
                personalized_questions.append(q)

        # 2. Generate Experience-specific questions from Resume
        experiences = structured.get("experience", [])
        for exp in experiences[:1]:
            company = exp.get("company")
            title = exp.get("job_title")
            if company and len(company) > 2:
                q = Question(
                    text=f"Describe your primary responsibilities and major technical achievements while serving as a {title or 'Developer'} at {company}.",
                    category="Behavioral",
                    difficulty="Medium",
                    sample_answer=f"Detail concrete project deliverables, teamwork, and problem-solving impact at {company}."
                )
                personalized_questions.append(q)

        # 3. Fetch standard role questions from DB
        role_questions = Question.query.filter(
            (Question.job_role_id == job_role.id) | (Question.job_role_id.is_(None))
        ).all()

        if role_questions:
            random.shuffle(role_questions)
            for rq in role_questions:
                if len(personalized_questions) >= count:
                    break
                personalized_questions.append(rq)

        # 4. Fill any remaining with baseline fallback questions
        if len(personalized_questions) < count:
            needed = count - len(personalized_questions)
            fallback_qs = QuestionGenerator._get_fallback_questions(job_role.title)
            for fq in fallback_qs[:needed]:
                personalized_questions.append(fq)

        return personalized_questions[:count]

    @staticmethod
    def _get_fallback_questions(role_title):
        return [
            Question(
                text=f"What are the core technical concepts and best practices required for a {role_title} role?",
                category="Technical",
                difficulty="Easy",
                sample_answer="Discuss core language features, OOP design patterns, error handling, and clean code principles."
            ),
            Question(
                text="Describe a challenging project you worked on. What obstacles did you encounter and how did you resolve them?",
                category="Behavioral",
                difficulty="Medium",
                sample_answer="Use the STAR method (Situation, Task, Action, Result) highlighting problem solving and teamwork."
            ),
            Question(
                text=f"How do you optimize system performance and database queries when building applications for {role_title}?",
                category="Technical",
                difficulty="Hard",
                sample_answer="Explain indexing, caching strategies, asynchronous processing, and profiling tools."
            ),
            Question(
                text="Imagine a production deployment fails unexpectedly during peak hours. Walk us through your debugging and triage process.",
                category="Scenario-based",
                difficulty="Hard",
                sample_answer="Check error logs, inspect monitoring metrics, revert recent changes if needed, and communicate with stakeholders."
            ),
            Question(
                text="Why are you interested in this role, and where do you see your technical skills progressing over the next two years?",
                category="HR",
                difficulty="Easy",
                sample_answer="Align career growth goals with modern technology trends, continuous learning, and impact."
            )
        ]
