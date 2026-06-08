from functools import wraps
from pathlib import Path
from uuid import uuid4

from flask import abort, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped_view


def save_uploaded_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    filename = secure_filename(file_storage.filename)
    suffix = Path(filename).suffix.lower()
    unique_name = f"{uuid4().hex}{suffix}"
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_storage.save(upload_dir / unique_name)
    return unique_name
