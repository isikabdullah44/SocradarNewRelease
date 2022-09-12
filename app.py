import shutil
from flask import Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from utils import package_utils

app = Flask(__name__)
app.config['UPLOAD_DIRECTORY'] = f'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['ALLOWED_EXTENSIONS'] = ['.mod', '.txt', '.json']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/pexatv/Desktop/SocradarNewRelease/data.db'
db = SQLAlchemy(app)


@app.route('/', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        user = UserTable.query.filter(UserTable.email == email).first()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            return redirect(url_for('home', user_id=user.user_id))

        flash(error)

    return render_template('login.html')


@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        password = request.form['password']
        email = request.form['email']
        error = None
        if not email:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                user_data = UserTable(
                    password=generate_password_hash(password),
                    email=email)
                db.session.add(user_data)
                db.session.commit()
            except db.IntegrityError:
                error = f"User {email} is already registered."
            else:
                return redirect(url_for("login"))

        flash(error)

    return render_template('register.html')


@app.route('/logout')
def logout():
    return "logout"


@app.route('/home/<user_id>')
def home(user_id):
    return render_template("home.html", user_id=user_id)


@app.route('/<user_id>/projects')
def projects(user_id):
    projects = UserProjectTable.query.filter(UserProjectTable.user_id == user_id).all()
    return render_template("index.html", projects=projects, user_id=user_id)


@app.route("/add/<user_id>", methods=["POST"])
def add_project(user_id):
    project_name = request.form.get("project_name")
    package_type = request.form.get("type")
    already_existed_packages = {item.package_name for item in PackageTable.query.all()}  # {'flask', 'sqlalchemy'}
    file = request.files['file']
    directory = project_name
    parent_dir = "/Users/pexatv/Desktop/SocradarNewRelease/uploads"
    path = os.path.join(parent_dir, directory)
    try:
        if not os.path.exists(path):
            os.mkdir(path)
            file.save(os.path.join(
                path,
                secure_filename(file.filename)
            ))
            file_name = file.filename
            extension = os.path.splitext(file.filename)[1].lower()
            package_utils.add_project(package_type, file_name, project_name, already_existed_packages, user_id)
            shutil.rmtree(path)
    except RequestEntityTooLarge:
        shutil.rmtree(path)
        print("hata")
        return 'File is larger than the 16MB limit.'

    return redirect(url_for("projects", user_id=user_id))


@app.route("/<user_id>/<project_name>")
def show_packages_of_project(user_id, project_name):
    package_type, links, datas, versions_dict = package_utils.show_packages_of_project(user_id, project_name)
    return render_template("detail.html", package_type=package_type,
                           links=links, datas=datas, project_name=project_name, versions_dict=versions_dict,
                           user_id=user_id)


@app.route("/delete/<user_id>/<project_name>")
def delete_project(user_id, project_name):
    package_utils.delete_project(user_id, project_name)
    return redirect(url_for("projects", user_id=user_id))


@app.route("/delete/<user_id>/<project_name>/<package_id>")
def delete_package_from_project(user_id, project_name, package_id):
    package_utils.delete_package_from_project(user_id, project_name, package_id)
    return redirect(url_for("show_packages_of_project", project_name=project_name, user_id=user_id))


@app.route("/add/<user_id>/<project_name>/<package_type>", methods=["POST"])
def add_package_to_project(user_id, project_name, package_type):
    package_utils.add_package_to_project(user_id, project_name, package_type)
    return redirect(url_for("show_packages_of_project", project_name=project_name, user_id=user_id))


class PackageTable(db.Model):
    package_id = db.Column(db.Integer, primary_key=True)
    package_name = db.Column(db.String(80))  #
    last_version = db.Column(db.Integer)  #
    package_type = db.Column(db.Integer)
    all_versions_of_project = db.Column(db.String())


class UserPackageTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    package_id = db.Column(db.Integer)  #
    current_version = db.Column(db.Integer)  #
    last_version = db.Column(db.Integer)  #
    project_name = db.Column(db.String(80))  #


class UserProjectTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    project_name = db.Column(db.String(80))
    package_type = db.Column(db.String(80))


class UserTable(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String)
    email = db.Column(db.String)


if __name__ == "__main__":
    app.run(debug=True)
