import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    # Minimum 6 characters
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""

def allowed_file(filename, allowed_extensions={'pdf'}):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
