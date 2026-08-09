import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import db
from models.resume import Resume
from models.skill import Skill, UserSkill
from models.job_role import JobRole
from services.resume_parser import ResumeParser
from services.skill_gap import SkillGapAnalyzer
from utils.helpers import get_safe_filename
from utils.validators import allowed_file

resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/upload-resume', methods=['GET', 'POST'])
@login_required
def upload_resume():
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file part in the request.', 'danger')
            return redirect(request.url)

        file = request.files['resume']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Invalid file extension. Only PDF files are accepted.', 'danger')
            return redirect(request.url)

        try:
            filename = get_safe_filename(file.filename)
            upload_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)

            # Parse Resume into Complete Structured JSON Data
            parsed_data = ResumeParser.parse_resume(file_path)

            contact = parsed_data.get("personal_information", {})
            raw_text = parsed_data.get("raw_text", "")

            # Save Resume record with structured JSON & completeness score
            resume = Resume(
                user_id=current_user.id,
                filename=filename,
                file_path=file_path,
                raw_text=raw_text,
                parsed_name=contact.get("name", ""),
                parsed_email=contact.get("email", ""),
                parsed_phone=contact.get("phone", ""),
                parsed_education=json.dumps(parsed_data.get("education", [])),
                parsed_experience=json.dumps(parsed_data.get("experience", [])),
                parsed_projects=json.dumps(parsed_data.get("projects", [])),
                parsed_certifications=json.dumps(parsed_data.get("certifications", [])),
                structured_json=json.dumps(parsed_data),
                completeness_score=parsed_data.get("completeness_score", 0.0)
            )
            db.session.add(resume)

            # Store extracted skills in UserSkill table
            skills_dict = parsed_data.get("skills", {})
            extracted_skill_names = []
            for cat_key, skill_list in skills_dict.items():
                if isinstance(skill_list, list):
                    for skill_name in skill_list:
                        if skill_name not in extracted_skill_names:
                            extracted_skill_names.append(skill_name)

            for name in extracted_skill_names:
                skill_obj = Skill.query.filter_by(name=name).first()
                if not skill_obj:
                    skill_obj = Skill(name=name, category="General")
                    db.session.add(skill_obj)
                    db.session.flush()

                existing_map = UserSkill.query.filter_by(user_id=current_user.id, skill_id=skill_obj.id).first()
                if not existing_map:
                    user_skill = UserSkill(user_id=current_user.id, skill_id=skill_obj.id, source='resume')
                    db.session.add(user_skill)

            db.session.commit()
            flash(f'Resume parsed successfully! Extracted {len(extracted_skill_names)} skills with {parsed_data.get("completeness_score", 0)}% completeness score.', 'success')
            return redirect(url_for('resume.resume_analysis'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error processing resume: {str(e)}', 'danger')

    return render_template('upload_resume.html')

@resume_bp.route('/resume-analysis')
@login_required
def resume_analysis():
    latest_resume = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).first()
    if not latest_resume:
        flash('Please upload your resume to view structured analysis.', 'warning')
        return redirect(url_for('resume.upload_resume'))

    structured = latest_resume.get_structured_data()
    return render_template('resume_analysis.html', resume=latest_resume, structured=structured)

@resume_bp.route('/skills', methods=['GET', 'POST'])
@login_required
def view_skills():
    if request.method == 'POST':
        new_skill_name = request.form.get('skill_name', '').strip()
        if new_skill_name:
            skill_obj = Skill.query.filter_by(name=new_skill_name).first()
            if not skill_obj:
                skill_obj = Skill(name=new_skill_name, category="Custom")
                db.session.add(skill_obj)
                db.session.flush()

            existing = UserSkill.query.filter_by(user_id=current_user.id, skill_id=skill_obj.id).first()
            if not existing:
                db.session.add(UserSkill(user_id=current_user.id, skill_id=skill_obj.id, source='manual'))
                db.session.commit()
                flash(f'Skill "{new_skill_name}" added successfully.', 'success')

    user_skills = current_user.skills.all()
    latest_resume = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).first()
    return render_template('skills.html', user_skills=user_skills, latest_resume=latest_resume)

@resume_bp.route('/skill-gap')
@login_required
def skill_gap():
    target_role = current_user.target_role
    user_skill_names = [us.skill.name for us in current_user.skills.all() if us.skill]
    required_skill_names = []
    
    if target_role:
        required_skill_names = [jrs.skill.name for jrs in target_role.role_skills if jrs.skill]

    analysis = SkillGapAnalyzer.analyze_gap(user_skill_names, required_skill_names)
    all_roles = JobRole.query.all()

    return render_template('skill_gap.html', analysis=analysis, target_role=target_role, all_roles=all_roles)
