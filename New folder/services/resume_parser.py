import os
import re
import pdfplumber

# Configurable Skill Dictionary categorized by domain
SKILL_TAXONOMY_CATEGORIES = {
    "programming_languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go", "Rust", 
        "Ruby", "PHP", "Swift", "Kotlin", "R", "Scala", "Dart", "MATLAB", "Perl", "Bash", "Shell"
    ],
    "frameworks": [
        "React", "Angular", "Vue", "Node.js", "Express", "Flask", "Django", "FastAPI", 
        "Spring Boot", "Next.js", "Nuxt.js", "Bootstrap", "Tailwind", "ASP.NET", "Laravel"
    ],
    "databases": [
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Oracle", "Cassandra", 
        "DynamoDB", "Elasticsearch", "Neo4j", "MariaDB", "Firebase"
    ],
    "cloud": [
        "AWS", "Azure", "GCP", "Google Cloud Platform", "Heroku", "Vercel", "Netlify", 
        "DigitalOcean", "OpenStack"
    ],
    "tools": [
        "Git", "GitHub", "GitLab", "Docker", "Kubernetes", "CI/CD", "Linux", "Unix", 
        "Terraform", "Ansible", "Jenkins", "Jira", "Webpack", "Postman", "Swagger", "Power BI", "Tableau", "Excel"
    ],
    "ai_ml": [
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "TensorFlow", 
        "PyTorch", "Pandas", "NumPy", "Scikit-learn", "Keras", "OpenCV", "Generative AI", 
        "LLM", "RAG", "Prompt Engineering", "OpenAI", "LangChain", "Hugging Face"
    ],
    "soft_skills": [
        "Leadership", "Communication", "Teamwork", "Problem Solving", "Critical Thinking", 
        "Time Management", "Project Management", "Agile", "Scrum", "Adaptability", "Collaboration"
    ]
}

SECTION_KEYWORDS = {
    "profile": ["PROFILE", "SUMMARY", "PROFESSIONAL SUMMARY", "CAREER SUMMARY", "ABOUT ME", "OBJECTIVE", "CAREER OBJECTIVE"],
    "skills": ["SKILLS", "TECHNICAL SKILLS", "CORE SKILLS", "TECHNOLOGIES", "COMPETENCIES", "SKILLS & EXPERTISE", "TECHNICAL PROFICIENCY"],
    "experience": ["EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT", "PROFESSIONAL EXPERIENCE", "WORK HISTORY", "EMPLOYMENT HISTORY", "CAREER HISTORY"],
    "education": ["EDUCATION", "ACADEMIC BACKGROUND", "ACADEMIC HISTORY", "QUALIFICATIONS", "EDUCATIONAL QUALIFICATIONS"],
    "projects": ["PROJECTS", "PERSONAL PROJECTS", "KEY PROJECTS", "ACADEMIC PROJECTS", "SELECTED PROJECTS"],
    "certifications": ["CERTIFICATIONS", "CERTIFICATES", "LICENSES", "LICENSES & CERTIFICATIONS", "COURSES", "TRAINING"],
    "languages": ["LANGUAGES", "LANGUAGES SPOKEN", "LANGUAGE PROFICIENCY"],
    "achievements": ["ACHIEVEMENTS", "AWARDS", "HONORS", "COMPETITIONS", "RECOGNITION", "ACCOMPLISHMENTS"]
}


class ResumeParser:
    @staticmethod
    def extract_pdf_text(file_path):
        """
        Extract readable text from all pages of a PDF file using pdfplumber.
        Handles multi-page, blank pages, and line break formatting gracefully.
        Returns friendly warning text if PDF is image-based or empty.
        """
        if not os.path.exists(file_path):
            return "File not found."

        text_content = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for idx, page in enumerate(pdf.pages):
                    page_text = page.extract_text(layout=False)
                    if page_text and page_text.strip():
                        text_content.append(page_text.strip())

            full_text = "\n\n".join(text_content)
            if not full_text or len(full_text.strip()) < 20:
                return "This PDF appears to be image-based or contains non-selectable text. OCR or a text-based PDF is recommended."

            return ResumeParser.clean_resume_text(full_text)

        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"

    @staticmethod
    def clean_resume_text(text):
        """Clean line breaks, strange spacing, carriage returns, and unicode control characters."""
        if not text:
            return ""

        # Normalize line endings
        cleaned = text.replace('\r\n', '\n').replace('\r', '\n')
        # Remove non-printable characters except standard tabs/newlines
        cleaned = re.sub(r'[^\x00-\x7F\u00A0-\u024F]+', ' ', cleaned)
        # Collapse multiple blank lines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        # Collapse extra horizontal spaces
        cleaned = re.sub(r'[ \t]{2,}', ' ', cleaned)

        return cleaned.strip()

    @staticmethod
    def detect_sections(clean_text):
        """
        Identify section boundaries in resume text.
        Returns dictionary mapping section key to list of text lines.
        """
        lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
        sections = {key: [] for key in SECTION_KEYWORDS.keys()}
        sections["header"] = []

        current_section = "header"

        for line in lines:
            line_upper = line.upper().strip(":#-—_ ")

            # Check if line matches a known section header
            matched_section = None
            for sec_key, kw_list in SECTION_KEYWORDS.items():
                if line_upper in kw_list or any(line_upper == kw or line_upper.startswith(kw + ":") for kw in kw_list):
                    matched_section = sec_key
                    break

            if matched_section:
                current_section = matched_section
            else:
                sections[current_section].append(line)

        return {k: "\n".join(v) for k, v in sections.items()}

    @staticmethod
    def extract_contact_information(full_text, header_text=""):
        """Use regex to extract Name, Email, Phone, Address, LinkedIn, GitHub, Portfolio."""
        contact = {
            "name": "",
            "email": "",
            "phone": "",
            "address": "",
            "linkedin": "",
            "github": "",
            "portfolio": ""
        }

        if not full_text:
            return contact

        combined_search = (header_text + "\n" + full_text[:1000])

        # 1. Email Extraction
        email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', combined_search)
        if email_match:
            contact["email"] = email_match.group(0)

        # 2. Phone Extraction
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', combined_search)
        if phone_match:
            contact["phone"] = phone_match.group(0).strip()

        # 3. LinkedIn URL
        linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?', combined_search, re.I)
        if linkedin_match:
            contact["linkedin"] = linkedin_match.group(0)

        # 4. GitHub URL
        github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+/?', combined_search, re.I)
        if github_match:
            contact["github"] = github_match.group(0)

        # 5. Portfolio / Website URL
        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', combined_search)
        for u in urls:
            if "linkedin.com" not in u.lower() and "github.com" not in u.lower():
                contact["portfolio"] = u
                break

        # 6. Name Extraction (First non-contact header line)
        header_lines = [l.strip() for l in header_text.split('\n') if l.strip()]
        if not header_lines:
            header_lines = [l.strip() for l in full_text.split('\n') if l.strip()]

        for l in header_lines[:5]:
            # Skip if line contains email, phone, or section keywords
            if "@" in l or re.search(r'\d{5,}', l) or "RESUME" in l.upper() or "CURRICULUM" in l.upper():
                continue
            if len(l) < 50:
                contact["name"] = re.sub(r'[^\w\s.-]', '', l).strip()
                break

        # 7. Address / Location (City, State / Country)
        loc_match = re.search(r'([A-Z][a-zA-Z\s]+,\s*[A-Z]{2}(?:\s+\d{5})?|[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z\s]+)', combined_search)
        if loc_match and "LinkedIn" not in loc_match.group(0):
            contact["address"] = loc_match.group(0).strip()

        return contact

    @staticmethod
    def extract_profile(section_text, full_text):
        """Extract Profile / Summary / Objective statement."""
        if section_text and len(section_text.strip()) > 10:
            return section_text.strip()
        
        # Fallback: look for summary paragraph near top of text
        lines = [l.strip() for l in full_text.split('\n') if l.strip()]
        for idx, line in enumerate(lines[:10]):
            if any(kw in line.upper() for kw in ["SUMMARY", "OBJECTIVE", "PROFILE", "ABOUT ME"]):
                return "\n".join(lines[idx+1:idx+4])
        return ""

    @staticmethod
    def extract_skills(section_text, full_text):
        """
        Extract categorized technical & soft skills against master taxonomy.
        Ensures deduplication and clean categorization.
        """
        search_text = (section_text + "\n" + full_text).upper()
        
        skills_categorized = {
            "technical": [],
            "programming_languages": [],
            "frameworks": [],
            "databases": [],
            "cloud": [],
            "tools": [],
            "ai_ml": [],
            "soft_skills": [],
            "other": []
        }

        all_found = set()

        for category_key, skill_list in SKILL_TAXONOMY_CATEGORIES.items():
            for skill in skill_list:
                # Regex boundary check
                pattern = r'\b' + re.escape(skill.upper()) + r'\b'
                if skill in ["C++", "C#"]:
                    pattern = r'\b' + re.escape(skill.upper())
                elif skill == "C":
                    pattern = r'\bC\b'

                if re.search(pattern, search_text):
                    if skill not in all_found:
                        all_found.add(skill)
                        if category_key in skills_categorized:
                            skills_categorized[category_key].append(skill)
                        else:
                            skills_categorized["technical"].append(skill)

        return skills_categorized

    @staticmethod
    def extract_education(section_text):
        """Extract degree, field of study, institution, dates, GPA/percentage."""
        education_list = []
        if not section_text:
            return education_list

        degree_patterns = [
            r'B\.?Tech|Bachelor[s]?\s+of\s+[A-Za-z\s]+|B\.?E\.?|B\.?Sc|B\.?A\.?',
            r'M\.?Tech|Master[s]?\s+of\s+[A-Za-z\s]+|M\.?E\.?|M\.?Sc|MBA|M\.?A\.?',
            r'Ph\.?D|Doctor\s+of\s+Philosophy',
            r'Diploma|Associate\s+Degree|High\s+School'
        ]

        lines = [l.strip() for l in section_text.split('\n') if l.strip()]
        current_entry = {}

        for line in lines:
            # Check for Degree
            degree_match = None
            for pat in degree_patterns:
                m = re.search(pat, line, re.I)
                if m:
                    degree_match = m.group(0)
                    break

            # Date Range check (e.g., 2020 - 2024 or 2024)
            date_match = re.search(r'\b(19|20)\d{2}\s*[-–—\s]\s*(19|20)\d{2}|\b(19|20)\d{2}\b', line)
            # GPA / Percentage check
            gpa_match = re.search(r'GPA\s*:?\s*([\d.]+/?\d*)|(\d{2,3}%|\b[\d.]+\s*CGPA\b)', line, re.I)

            if degree_match or date_match:
                if current_entry and (current_entry.get("degree") or current_entry.get("institution")):
                    education_list.append(current_entry)
                    current_entry = {}

                current_entry = {
                    "degree": degree_match or line[:60],
                    "field": "Computer Science & Engineering" if "computer" in line.lower() else "",
                    "institution": line if not degree_match else "University / Institution",
                    "start_year": date_match.group(0).split('-')[0].strip() if date_match and '-' in date_match.group(0) else (date_match.group(0) if date_match else ""),
                    "end_year": date_match.group(0).split('-')[-1].strip() if date_match and '-' in date_match.group(0) else "",
                    "gpa": gpa_match.group(0) if gpa_match else "",
                    "location": ""
                }
            elif current_entry:
                if not current_entry["institution"] or current_entry["institution"] == "University / Institution":
                    current_entry["institution"] = line[:100]

        if current_entry and (current_entry.get("degree") or current_entry.get("institution")):
            education_list.append(current_entry)

        return education_list

    @staticmethod
    def extract_experience(section_text):
        """Extract Work Experience entries (Company, Job Title, Start/End dates, Responsibilities)."""
        experience_list = []
        if not section_text:
            return experience_list

        lines = [l.strip() for l in section_text.split('\n') if l.strip()]
        current_job = None

        job_title_keywords = ["Developer", "Engineer", "Analyst", "Manager", "Lead", "Architect", "Intern", "Consultant", "Specialist", "Administrator"]

        for line in lines:
            date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|[0-9]{4})\b.*?[-–—\s].*?\b(Present|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|[0-9]{4})\b', line, re.I)
            is_title = any(kw in line for kw in job_title_keywords)

            if date_match or is_title:
                if current_job:
                    experience_list.append(current_job)

                start_date = ""
                end_date = ""
                if date_match:
                    parts = date_match.group(0).split('-')
                    start_date = parts[0].strip()
                    end_date = parts[1].strip() if len(parts) > 1 else "Present"

                current_job = {
                    "company": line.split('-')[0].strip() if '-' in line else line[:60],
                    "job_title": line if is_title else "Software Engineer / Professional",
                    "start_date": start_date,
                    "end_date": end_date,
                    "location": "",
                    "responsibilities": [],
                    "achievements": [],
                    "technologies": []
                }
            elif current_job:
                if line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                    current_job["responsibilities"].append(line.lstrip('•-*123456789. ').strip())
                else:
                    current_job["responsibilities"].append(line)

        if current_job:
            experience_list.append(current_job)

        return experience_list

    @staticmethod
    def extract_projects(section_text):
        """Extract Project entries (Name, Description, Technologies used, URL)."""
        projects_list = []
        if not section_text:
            return projects_list

        lines = [l.strip() for l in section_text.split('\n') if l.strip()]
        current_proj = None

        for line in lines:
            url_match = re.search(r'https?://[^\s]+|github\.com/[^\s]+', line, re.I)

            if "technologies" in line.lower() or "tech stack" in line.lower():
                if current_proj:
                    techs = [t.strip() for t in line.split(':')[-1].split(',')]
                    current_proj["technologies"].extend(techs)
            elif line.startswith(('•', '-', '*')):
                if current_proj:
                    current_proj["responsibilities"].append(line.lstrip('•-* ').strip())
            else:
                # Check if this line looks like a new project header (or first line)
                if not current_proj or (len(line) < 80 and '|' in line):
                    if current_proj:
                        projects_list.append(current_proj)
                    current_proj = {
                        "name": line.split('|')[0].strip() if '|' in line else line[:60],
                        "description": "",
                        "technologies": [],
                        "responsibilities": [],
                        "results": "",
                        "url": url_match.group(0) if url_match else ""
                    }
                else:
                    if current_proj:
                        current_proj["description"] = (current_proj["description"] + " " + line).strip()

        if current_proj:
            projects_list.append(current_proj)

        return projects_list

    @staticmethod
    def extract_certifications(section_text):
        """Extract Certifications (Name, Issuing Organization, Dates, ID, URL)."""
        cert_list = []
        if not section_text:
            return cert_list

        lines = [l.strip() for l in section_text.split('\n') if l.strip()]
        for line in lines:
            if len(line) > 5:
                org = "AWS" if "AWS" in line else ("Google" if "Google" in line else ("Microsoft" if "Microsoft" in line else "Certified"))
                cert_list.append({
                    "name": line[:80],
                    "issuing_organization": org,
                    "issue_date": "",
                    "expiry_date": "",
                    "credential_id": "",
                    "credential_url": ""
                })
        return cert_list

    @staticmethod
    def extract_languages(section_text, full_text):
        """Extract Spoken Languages and Proficiency."""
        lang_list = []
        known_languages = ["English", "Spanish", "French", "German", "Mandarin", "Hindi", "Japanese", "Chinese", "Arabic", "Portuguese", "Russian"]
        
        search_text = (section_text + "\n" + full_text)
        for lang in known_languages:
            if re.search(r'\b' + lang + r'\b', search_text, re.I):
                lang_list.append({
                    "language": lang,
                    "proficiency": "Professional Working"
                })
        return lang_list

    @staticmethod
    def extract_achievements(section_text):
        """Extract Achievements, Awards, Competitions."""
        ach_list = []
        if not section_text:
            return ach_list

        lines = [l.strip() for l in section_text.split('\n') if l.strip()]
        for line in lines:
            ach_list.append({
                "achievement": line[:120],
                "award": "Recognized Accomplishment",
                "competition": "",
                "recognition": ""
            })
        return ach_list

    @staticmethod
    def calculate_quality_score(parsed_data):
        """
        Calculate Resume Completeness Score (0-100%) and missing section list.
        Weights:
        - Personal Information: 10%
        - Profile: 10%
        - Skills: 15%
        - Education: 15%
        - Experience: 20%
        - Projects: 15%
        - Certifications: 5%
        - Languages: 5%
        - Achievements: 5%
        """
        score = 0.0
        missing = []

        # Personal Info (10%)
        personal = parsed_data.get("personal_information", {})
        if personal.get("name") and personal.get("email"):
            score += 10.0
        else:
            missing.append("Personal Information")

        # Profile (10%)
        if parsed_data.get("profile"):
            score += 10.0
        else:
            missing.append("Profile / Summary")

        # Skills (15%)
        skills = parsed_data.get("skills", {})
        total_skills = sum(len(v) for v in skills.values() if isinstance(v, list))
        if total_skills >= 5:
            score += 15.0
        elif total_skills > 0:
            score += 8.0
        else:
            missing.append("Skills")

        # Education (15%)
        if parsed_data.get("education"):
            score += 15.0
        else:
            missing.append("Education")

        # Experience (20%)
        if parsed_data.get("experience"):
            score += 20.0
        else:
            missing.append("Work Experience")

        # Projects (15%)
        if parsed_data.get("projects"):
            score += 15.0
        else:
            missing.append("Projects")

        # Certifications (5%)
        if parsed_data.get("certifications"):
            score += 5.0
        else:
            missing.append("Certifications")

        # Languages (5%)
        if parsed_data.get("languages"):
            score += 5.0
        else:
            missing.append("Languages")

        # Achievements (5%)
        if parsed_data.get("achievements"):
            score += 5.0
        else:
            missing.append("Achievements")

        return round(score, 1), missing

    @staticmethod
    def parse_resume(file_path):
        """
        Main entry point function.
        Parses PDF file and returns complete structured dictionary.
        """
        raw_text = ResumeParser.extract_pdf_text(file_path)

        if "Error extracting text" in raw_text or "image-based" in raw_text:
            return {
                "personal_information": {"name": "", "email": "", "phone": "", "address": "", "linkedin": "", "github": "", "portfolio": ""},
                "profile": raw_text,
                "skills": {"technical": [], "programming_languages": [], "frameworks": [], "databases": [], "cloud": [], "tools": [], "ai_ml": [], "soft_skills": [], "other": []},
                "education": [],
                "experience": [],
                "projects": [],
                "certifications": [],
                "languages": [],
                "achievements": [],
                "completeness_score": 0.0,
                "missing_sections": ["All Sections (Image-based PDF or parsing failure)"],
                "raw_text": raw_text
            }

        sections = ResumeParser.detect_sections(raw_text)

        contact_info = ResumeParser.extract_contact_information(raw_text, sections.get("header", ""))
        profile = ResumeParser.extract_profile(sections.get("profile", ""), raw_text)
        skills = ResumeParser.extract_skills(sections.get("skills", ""), raw_text)
        education = ResumeParser.extract_education(sections.get("education", ""))
        experience = ResumeParser.extract_experience(sections.get("experience", ""))
        projects = ResumeParser.extract_projects(sections.get("projects", ""))
        certifications = ResumeParser.extract_certifications(sections.get("certifications", ""))
        languages = ResumeParser.extract_languages(sections.get("languages", ""), raw_text)
        achievements = ResumeParser.extract_achievements(sections.get("achievements", ""))

        structured = {
            "personal_information": contact_info,
            "profile": profile,
            "skills": skills,
            "education": education,
            "experience": experience,
            "projects": projects,
            "certifications": certifications,
            "languages": languages,
            "achievements": achievements,
            "raw_text": raw_text
        }

        score, missing = ResumeParser.calculate_quality_score(structured)
        structured["completeness_score"] = score
        structured["missing_sections"] = missing

        return structured
