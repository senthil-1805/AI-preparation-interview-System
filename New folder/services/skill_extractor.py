import re

# Configurable master list of skills and categories
DEFAULT_SKILL_TAXONOMY = {
    "Programming Languages": ["Python", "Java", "C", "C++", "JavaScript", "TypeScript", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin"],
    "Web Frameworks": ["Flask", "Django", "React", "Node.js", "Express", "Vue", "Angular", "Next.js", "FastAPI", "Spring Boot", "HTML", "CSS", "Bootstrap", "Tailwind"],
    "Databases": ["SQL", "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Oracle", "Cassandra"],
    "Cloud & DevOps": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Git", "GitHub", "CI/CD", "Linux", "Terraform"],
    "AI & Data Science": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn", "Power BI", "Tableau", "Generative AI", "LLM", "RAG", "Prompt Engineering", "OpenAI", "LangChain"]
}

class SkillExtractor:
    def __init__(self, taxonomy=None):
        self.taxonomy = taxonomy or DEFAULT_SKILL_TAXONOMY

    def get_all_configurable_skills(self):
        """Returns flattened list of all known skills."""
        all_skills = []
        for cat, skills in self.taxonomy.items():
            all_skills.extend(skills)
        return all_skills

    def extract_skills(self, text):
        """Matches text against the skill taxonomy returning found skills."""
        if not text:
            return []

        extracted_skills = []
        text_upper = text.upper()

        for category, skills in self.taxonomy.items():
            for skill in skills:
                # Use word boundary or specific pattern matching for accuracy
                pattern = r'\b' + re.escape(skill.upper()) + r'\b'
                # Special check for C++ or C#
                if skill == "C++":
                    pattern = r'\bC\+\+\b|C\+\+'
                elif skill == "C":
                    pattern = r'\bC\b'
                elif skill == "RAG":
                    pattern = r'\bRAG\b'

                if re.search(pattern, text_upper):
                    if skill not in extracted_skills:
                        extracted_skills.append(skill)

        return sorted(extracted_skills)
