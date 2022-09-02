import shutil
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
import os

from utils import package_utils

app = Flask(__name__)
app.config['UPLOAD_DIRECTORY'] = f'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['ALLOWED_EXTENSIONS'] = ['.mod', '.txt', '.json']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/pexatv/Desktop/SocradarNewRelease/data.db'
db = SQLAlchemy(app)


@app.route('/')
def index():
    project_name_data = UserProjectTable.query.all()
    return render_template("index.html", project_name_data=project_name_data)

@app.route('/login')
def login():
    return "login"


@app.route('/logout')
def logout():
    return "logout"


@app.route('/sign-up')
def sign_up():
    return "signup"


@app.route("/<project_name>")
def show_packages_of_project(project_name):
    package_type, links, datas = package_utils.show_packages_of_project(project_name)
    return render_template("detail.html", package_type=package_type,
                           links=links, datas=datas, project_name=project_name)


@app.route("/delete/<project_name>")
def delete_project(project_name):
    package_utils.delete_project(project_name)
    return redirect(url_for("index"))


@app.route("/delete/<project_name>/<package_id>")
def delete_package_from_project(project_name, package_id):
    package_utils.delete_package_from_project(project_name, package_id)
    return redirect(url_for("show_packages_of_project", project_name=project_name))


@app.route("/add/<project_name>/<package_type>", methods=["POST"])
def add_package_to_project(project_name, package_type):
    package_utils.add_package_to_project(project_name, package_type)
    return redirect(url_for("show_packages_of_project", project_name=project_name))


@app.route("/add", methods=["POST"])
def add_project():
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
            package_utils.add_project(package_type, file_name, project_name, already_existed_packages)
            shutil.rmtree(path)
    except RequestEntityTooLarge:
        shutil.rmtree(path)
        print("hata")
        return 'File is larger than the 16MB limit.'

    return redirect(url_for("index"))


class PackageTable(db.Model):
    package_id = db.Column(db.Integer, primary_key=True)
    package_name = db.Column(db.String(80))  #
    last_version = db.Column(db.Integer)  #
    package_type = db.Column(db.Integer)


class UserPackageTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    package_id = db.Column(db.Integer)  #
    current_version = db.Column(db.Integer)  #
    last_version = db.Column(db.Integer)  #
    project_name = db.Column(db.String(80))  #


class UserProjectTable(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(80))
    package_type = db.Column(db.String(80))


class UserTable(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80))


if __name__ == "__main__":
    app.run(debug=True)
