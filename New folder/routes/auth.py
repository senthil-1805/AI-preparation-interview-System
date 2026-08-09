from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
from models.job_role import JobRole
from utils.validators import validate_email, validate_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    job_roles = JobRole.query.all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        target_role_id = request.form.get('target_role_id')

        # Validation
        if not name or not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('register.html', job_roles=job_roles)

        if not validate_email(email):
            flash('Invalid email format.', 'danger')
            return render_template('register.html', job_roles=job_roles)

        is_valid, pwd_msg = validate_password(password)
        if not is_valid:
            flash(pwd_msg, 'danger')
            return render_template('register.html', job_roles=job_roles)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', job_roles=job_roles)

        existing_user = User.query.filter_by(email=email.lower()).first()
        if existing_user:
            flash('Email address is already registered. Please login.', 'warning')
            return redirect(url_for('auth.login'))

        # Create User
        user = User(
            name=name,
            email=email.lower(),
            target_role_id=int(target_role_id) if target_role_id else None
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login to continue.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error registering user: {str(e)}', 'danger')

    return render_template('register.html', job_roles=job_roles)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('auth.login'))
