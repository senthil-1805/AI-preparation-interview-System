import unittest
from services.resume_parser import ResumeParser
from services.skill_gap import SkillGapAnalyzer
from utils.validators import allowed_file

class ResumeTestCase(unittest.TestCase):
    def test_allowed_file(self):
        self.assertTrue(allowed_file('my_resume.pdf'))
        self.assertFalse(allowed_file('resume.docx'))
        self.assertFalse(allowed_file('script.exe'))

    def test_structured_resume_parsing(self):
        sample_resume_text = """
        John Doe
        john.doe@example.com | +1 (555) 123-4567 | San Francisco, CA
        https://linkedin.com/in/johndoe | https://github.com/johndoe

        PROFILE
        Experienced Senior Software Engineer specializing in Python, Flask, SQL, Docker, and AI/ML applications.

        SKILLS
        Python, JavaScript, TypeScript, Flask, React, Node.js, PostgreSQL, Docker, AWS, Machine Learning, Deep Learning, Git, Communication

        WORK EXPERIENCE
        Tech Corp - Senior Python Developer
        2022 - Present | San Francisco, CA
        • Engineered high-performance REST APIs using Flask and PostgreSQL.
        • Deployed Docker containers to AWS ECS with 99.9% uptime.

        EDUCATION
        B.Tech in Computer Science and Engineering
        University of California
        2018 - 2022 | GPA: 3.9/4.0

        PROJECTS
        AI Interview Preparation System | https://github.com/johndoe/interview-ai
        Technologies: Python, Flask, SQL, NLP
        Built full-stack AI mock interview platform featuring automated PDF resume parser.

        CERTIFICATIONS
        AWS Certified Solutions Architect - Amazon Web Services

        LANGUAGES
        English - Native, Spanish - Professional Working

        ACHIEVEMENTS
        1st Place Winner - Global AI Hackathon 2024
        """

        clean_text = ResumeParser.clean_resume_text(sample_resume_text)
        sections = ResumeParser.detect_sections(clean_text)

        # Contact Info
        contact = ResumeParser.extract_contact_information(clean_text, sections.get("header", ""))
        self.assertEqual(contact["email"], "john.doe@example.com")
        self.assertIn("555", contact["phone"])
        self.assertIn("linkedin.com", contact["linkedin"])

        # Skills
        skills = ResumeParser.extract_skills(sections.get("skills", ""), clean_text)
        self.assertIn("Python", skills["programming_languages"])
        self.assertIn("Flask", skills["frameworks"])
        self.assertIn("Docker", skills["tools"])

        # Education
        education = ResumeParser.extract_education(sections.get("education", ""))
        self.assertTrue(len(education) > 0)
        self.assertIn("B.Tech", education[0]["degree"])

        # Experience
        experience = ResumeParser.extract_experience(sections.get("experience", ""))
        self.assertTrue(len(experience) > 0)

        # Projects
        projects = ResumeParser.extract_projects(sections.get("projects", ""))
        self.assertTrue(len(projects) > 0)
        self.assertIn("AI Interview", projects[0]["name"])

        # Quality Score
        score, missing = ResumeParser.calculate_quality_score({
            "personal_information": contact,
            "profile": "Profile text",
            "skills": skills,
            "education": education,
            "experience": experience,
            "projects": projects,
            "certifications": [{"name": "AWS Certified"}],
            "languages": [{"language": "English"}],
            "achievements": [{"achievement": "Winner"}]
        })
        self.assertEqual(score, 100.0)

    def test_skill_gap_analysis(self):
        user_skills = ['Python', 'Flask', 'SQL']
        required_skills = ['Python', 'Flask', 'SQL', 'Docker', 'AWS']

        gap = SkillGapAnalyzer.analyze_gap(user_skills, required_skills)
        self.assertEqual(len(gap['matching_skills']), 3)
        self.assertEqual(len(gap['missing_skills']), 2)
        self.assertEqual(gap['coverage_pct'], 60.0)

if __name__ == '__main__':
    unittest.main()
