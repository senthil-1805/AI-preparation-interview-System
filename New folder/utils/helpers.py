import os
import uuid
from werkzeug.utils import secure_filename

def get_safe_filename(original_filename):
    ext = os.path.splitext(original_filename)[1].lower()
    clean_name = secure_filename(os.path.splitext(original_filename)[0])
    unique_id = uuid.uuid4().hex[:8]
    return f"{clean_name}_{unique_id}{ext}"

def format_percentage(val):
    try:
        return f"{float(val):.1f}%"
    except (ValueError, TypeError):
        return "0.0%"
