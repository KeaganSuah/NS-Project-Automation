from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from sqlalchemy import exc
from flask_login import login_user, login_required, logout_user, current_user
from parade_state_function import branches_string, dropdown_branch

auth = Blueprint('auth', __name__)


# login page
@auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        # login inputs
        first_name = request.form.get('firstName')
        password = request.form.get('password')
        # finding user in website database
        user = User.query.filter_by(first_name=first_name).first()
        if user:
            # check if user passwords matches
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.index'))
            else:
                flash('Incorrect Password, try again.', category='error')
        # check if user exist in database
        else:
            flash('Wrong details have been entered, Please enter the correct information.', category='error')
    return render_template("login.html", user=current_user)


# log user out of website
@auth.route('/logout')
@login_required
def logout():
    flash('Your account has been logged out.', category='success')
    logout_user()
    return redirect(url_for('auth.login'))


# admin sign up page
@auth.route('/sign-up', methods=["GET", "POST"])
@login_required
def sign_up():
    # current login user only can sign up what is authorized for them
    user_name = current_user.first_name
    user = User.query.filter_by(first_name=user_name).first()
    branch_access = user.branch
    if request.method == 'POST':
        # get particulars for new user
        first_name = request.form.get('firstName')
        branch = request.form.get('branch')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter_by(first_name=first_name).first()
        if user:
            flash('Name already exist', category='error')
        elif len(first_name) < 4:
            flash('Name must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('Name must be greater than 1 characters.', category='error')
        elif password1 != password2:
            flash('Password don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be greater than 6 characters.', category='error')
        else:
            new_user = User(first_name=first_name, branch=branch, password=generate_password_hash(
                password1, method='sha256'))
            try:
                db.session.add(new_user)
                db.session.commit()
            except exc.IntegrityError:
                db.session.rollback()
            flash('Account created!', category='success')
            return redirect(url_for('views.index'))
    return render_template("sign_up.html", user=current_user, branches_string=branches_string, dropdown_branch=dropdown_branch, branch_access=branch_access)
