from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from .models import get_user_by_email, get_user_by_id, insert_user, update_user
import os
import random

auth = Blueprint('auth', __name__)
UPLOAD_FOLDER = "website/static/profile_pictures/"
ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg"]

class DBUser(UserMixin):
    def __init__(self, user_dict):
        self.id = user_dict["id"]
        self.email = user_dict["email"]
        self.first_name = user_dict["first_name"]
        self.last_name = user_dict["last_name"]
        self.profile_picture = user_dict.get("profile_picture", "default_profile_photo.jpg")
        self.bio = user_dict.get("bio", "")

def allowed_file(filename):
    return "." in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@auth.route("/", methods=['GET','POST'])
@auth.route("/login", methods=['GET','POST'])
def login_page():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user_dict = get_user_by_email(email)

        if user_dict and check_password_hash(user_dict["password"], password):
            user_obj = DBUser(user_dict)
            login_user(user_obj, remember=True)
            flash("Logged in successfully.", "success")
            return redirect("/home/")
        elif user_dict:
            flash("Incorrect password.", "error")
        else:
            flash("Email not registered.", "error")

    return render_template("login_page.html", page="Login", user=current_user)

@auth.route("/sign-up", methods=['GET','POST'])
def signup_page():
    if current_user.is_authenticated:
        return redirect(url_for("views.home"))

    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user_dict = get_user_by_email(email)

        if user_dict:
            flash("Email already registered.", "error")
        elif len(first_name) < 2:
            flash("First Name too short.", "error")
        elif len(last_name) < 1:
            flash("Last Name required.", "error")
        elif len(email) < 5:
            flash("Email too short.", "error")
        elif password1 != password2:
            flash("Passwords don't match.", "error")
        elif len(password1) < 7:
            flash("Password too short.", "error")
        else:
            hashed_password = generate_password_hash(password1, method="pbkdf2:sha256")
            insert_user(first_name, last_name, email, hashed_password)
            # Auto-login after signup
            user_dict = get_user_by_email(email)
            login_user(DBUser(user_dict))
            flash("Account created and logged in!", "success")
            return redirect(url_for("views.home"))

        return render_template("signup_page.html", page="Sign Up", user=current_user,
                               form_first_name=first_name, form_last_name=last_name, form_email=email)

    return render_template("signup_page.html", page="Sign Up", user=current_user)
