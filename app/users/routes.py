from flask import request, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user
from . import users_bp  # Import the blueprint object

@users_bp.route("/login", methods=["GET", "POST"])
def login():
    from .forms import LoginForm  # Delay import
    from app.models import User  # Delay import

    form = LoginForm()

    # If the form is valid, handle Log In
    if form.validate_on_submit():
        if form.login.data:  # Log In button clicked
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for("home.index"))
            flash("Invalid username or password.", "danger")

    return render_template("login.html", form=form)

@users_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('users.login'))  # Use blueprint prefix

@users_bp.route("/register", methods=["GET", "POST"])
def register():
    from .forms import RegistrationForm  # Delay import
    from app.models import User  # Delay import
    from app import db  # Delay import

    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if the username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for('users.register'))
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already exists. Please choose a different one.", "danger")
            return redirect(url_for('users.register'))

        # Create a new user
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('users.login'))

    return render_template("register.html", form=form)
