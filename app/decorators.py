from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "danger")
                return redirect(url_for("users.login"))
            if current_user.role not in roles:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for("home.index"))
            return func(*args, **kwargs)
        return wrapper
    return decorator
