from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.job_role import JobRole

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    job_roles = JobRole.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        target_role_id = request.form.get('target_role_id')

        if name:
            current_user.name = name
        if target_role_id:
            current_user.target_role_id = int(target_role_id)

        try:
            db.session.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('profile.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')

    return render_template('profile.html', job_roles=job_roles)
