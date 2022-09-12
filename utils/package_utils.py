from flask import request
from sqlalchemy import and_

import app
import go_lib
import node_lib
import python_lib
import json


def add_project(package_type, file_name, project_name, already_existed_packages, user_id):
    app_by_package_type = {
        "go": {
            "for_current_versions": go_lib.current_versions,
            "for_package_search": go_lib.go_package_search,
            "for_versions_of_packages": go_lib.go_all_versions_of_packages
        },
        "node": {
            "for_current_versions": node_lib.current_versions,
            "for_package_search": node_lib.node_package_search,
            "for_versions_of_packages": node_lib.node_all_versions_of_packages

        },
        "python": {
            "for_current_versions": python_lib.current_versions,
            "for_package_search": python_lib.python_package_search,
            "for_versions_of_packages": python_lib.python_all_versions_of_packages

        }
    }
    current_versions_of_packages = app_by_package_type[package_type]["for_current_versions"](file_name, project_name)
    for package_name in current_versions_of_packages:
        current_version = current_versions_of_packages[package_name]
        if package_name not in already_existed_packages:  # 0'ı anlaşılır  hale getir
            already_existed_packages.add(package_name)
            all_versions_of_package = app_by_package_type[package_type]["for_versions_of_packages"](package_name)
            last_version = app_by_package_type[package_type]["for_package_search"](package_name)
            package_table_data = app.PackageTable(package_name=package_name, last_version=last_version,
                                                  package_type=package_type,
                                                  all_versions_of_project=all_versions_of_package)
            app.db.session.add(package_table_data)
            item = app.PackageTable.query.filter(app.PackageTable.package_name == package_name).first()
            package_id = item.package_id
            user_package_table_data = app.UserPackageTable(package_id=package_id, last_version=last_version,
                                                           project_name=project_name, current_version=current_version,
                                                           user_id=user_id)
            app.db.session.add(user_package_table_data)
        else:
            item = app.PackageTable.query.filter(app.PackageTable.package_name == package_name).first()
            package_id = item.package_id
            last_version = item.last_version
            user_package_table_data = app.UserPackageTable(package_id=package_id, current_version=current_version,
                                                           last_version=last_version,
                                                           project_name=project_name,
                                                           user_id=user_id)
            app.db.session.add(user_package_table_data)
    project_name_type_data = app.UserProjectTable(user_id=user_id, project_name=project_name, package_type=package_type)
    app.db.session.add(project_name_type_data)
    app.db.session.commit()


def delete_project(user_id, project_name):
    project = app.UserProjectTable.query.filter(app.UserProjectTable.user_id == user_id,
                                                app.UserProjectTable.project_name == project_name).first()
    packages = app.UserPackageTable.query.filter(app.UserPackageTable.user_id == int(user_id),
                                                 app.UserPackageTable.project_name == project_name).all()
    for package in packages:
        app.db.session.delete(package)
    app.db.session.delete(project)
    app.db.session.commit()


def show_packages_of_project(user_id, project_name):
    datas = {}
    versions_dict = {}
    links = {
        'node': f'https://www.npmjs.com/package/',
        'python': f'https://pypi.org/project/',
        'go': f'https://pkg.go.dev/'
    }
    results = app.UserPackageTable.query.filter(app.UserPackageTable.project_name == project_name,
                                                app.UserPackageTable.user_id == user_id).all()
    project = app.UserProjectTable.query.filter(app.UserProjectTable.project_name == project_name,
                                                app.UserProjectTable.user_id == user_id).first()
    package_type = project.package_type
    for result in results:
        data = app.PackageTable.query.filter(app.PackageTable.package_id == result.package_id).first()
        versions = json.loads(data.all_versions_of_project)
        try:
            index_of_current_version = versions.projects(result.current_version)
            datas[result] = data
            needed_versions = []
            while index_of_current_version < len(versions):
                needed_versions.append(versions[index_of_current_version])
                index_of_current_version += 1
            versions_dict[result] = needed_versions
        except:
            datas[result] = data
            needed_versions = [result.current_version]
            versions_dict[result] = needed_versions

    return package_type, links, datas, versions_dict


def add_package_to_project(user_id, project_name, package_type):
    package_name = request.form.get("package_name")
    apps = {
        "node": node_lib.node_package_search,
        "python": python_lib.python_package_search,
        "go": go_lib.go_package_search

    }
    already_existed_packages = {item.package_name for item in app.PackageTable.query.all()}
    if package_name in already_existed_packages:
        item = app.PackageTable.query.filter(app.PackageTable.package_name == package_name).first()
        package_id = item.package_id
        last_version = item.last_version
        user_package_table_data = app.UserPackageTable(package_id=package_id, last_version=last_version,
                                                       project_name=project_name, user_id=user_id)
        app.db.session.add(user_package_table_data)
    else:
        already_existed_packages.add(package_name)
        last_version = apps[package_type](package_name)
        package_table_data = app.PackageTable(package_name=package_name, last_version=last_version,
                                              package_type=package_type)
        app.db.session.add(package_table_data)
        item = app.PackageTable.query.filter(app.PackageTable.package_name == package_name).first()
        package_id = item.package_id
        user_package_table_data = app.UserPackageTable(package_id=package_id, last_version=last_version,
                                                       project_name=project_name, user_id=user_id)
        app.db.session.add(user_package_table_data)
    app.db.session.commit()


def delete_package_from_project(user_id, project_name, package_id):
    project = app.UserPackageTable.query.filter_by(project_name=project_name, package_id=package_id,
                                                   user_id=user_id).first()
    app.db.session.delete(project)
    app.db.session.commit()
