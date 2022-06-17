from flask import Blueprint, request, flash, redirect, url_for, abort
from .models import UserModel
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user
from urllib.parse import urlparse, urljoin


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


auth = Blueprint('auth', __name__)

# Login Page
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.values.get('email')
        password = request.values.get('password')
        next = request.args.get('next')

        if not is_safe_url(next):
            return abort(400, description='Unsafe Url')

        user = UserModel.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(next or url_for('views.home', username=user))
            else:
                return "Login Page: Incorrect password, try again."
        else:
            return "Login Page: This user does not exist "

    return "This is the Login Page"

# Logout Page
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return "This is the Logout Page"

# Sign-up Page
@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.values.get('email')
        fname = request.values.get('fname')
        lname = request.values.get('lname')
        password = request.values.get('password')

        user = UserModel.query.filter_by(email=email).first()
        if user:
            return ('Sign up Page: Email already exists.')
        else:
            new_user = UserModel(email=email, fname=fname, lname=lname, password=generate_password_hash(
                password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for('views.home', username=new_user))

    return "This is the Sign up Page"
