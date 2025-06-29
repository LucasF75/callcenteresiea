from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.forms import RegisterForm, LoginForm
from app import db

auth = Blueprint('auth', __name__)


from flask import flash

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Aucun utilisateur trouvé avec cet email.", "error")
        elif not check_password_hash(user.password, password):
            flash("Mot de passe incorrect.", "error")
        else:
            login_user(user)
            flash("Connexion réussie !", "success")
            return redirect(url_for('main.home'))
    elif form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()} : {error}", "error")

    return render_template('login.html', form=form)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        name = form.username.data
        password = form.password.data

        if User.query.filter_by(email=email).first():
            flash('Email déjà utilisé.', 'error')
            return redirect(url_for('auth.signup'))  # ✅ on reste sur signup

        new_user = User(
            email=email,
            name=name,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('main.home'))

    # Cas où le formulaire n'est pas valide
    elif form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()} : {error}", 'error')

    return render_template('signup.html', form=form)




@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
