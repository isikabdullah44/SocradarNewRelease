from flask import request
import app
import go_lib
import node_lib
import python_lib


def show_packages_of_project(project_name):
    datas = {}
    links = {
        'node': f'https://www.npmjs.com/package/',
        'python': f'https://pypi.org/project/',
        'go': f'https://pkg.go.dev/'
    }
    results = app.UserPackageTable.query.filter(app.UserPackageTable.project_name == project_name).all()
    project = app.UserProjectTable.query.filter(app.UserProjectTable.project_name == project_name).first()
    package_type = project.package_type
    for result in results:
        data = app.PackageTable.query.filter(app.PackageTable.package_id == result.package_id).first()
        datas[result] = data.package_name
    return package_type, links, datas


def delete_project(project_name):
    project = app.UserProjectTable.query.filter_by(project_name=project_name).first()
    packages = app.UserPackageTable.query.filter_by(project_name=project_name).all()
    for package in packages:
        app.db.session.delete(package)
    app.db.session.delete(project)
    app.db.session.commit()


def add_project(package_type, file_name, project_name, already_existed_packages):
    app_by_package_type = {
        "go": {
            "for_current_versions": go_lib.current_versions,
            "for_package_search": go_lib.go_package_search
        },
        "node": {
            "for_current_versions": node_lib.current_versions,
            "for_package_search": node_lib.node_package_search
        },
        "python": {
            "for_current_versions": python_lib.current_versions,
            "for_package_search": python_lib.python_package_search
        }
    }
    current_versions_of_packages = app_by_package_type[package_type]["for_current_versions"](file_name, project_name)
    for package_name in current_versions_of_packages:
        current_version = current_versions_of_packages[package_name]
        if package_name not in already_existed_packages:  # 0'ı anlaşılır  hale getir
            already_existed_packages.add(package_name)
            last_version = app_by_package_type[package_type]["for_package_search"](package_name)
            package_table_data = app.PackageTable(package_name=package_name, last_version=last_version,
                                                  package_type=package_type)
            app.db.session.add(package_table_data)
            item = app.PackageTable.query.filter(app.PackageTable.package_name == package_name).first()
            package_id = item.package_id
            user_package_table_data = app.UserPackageTable(package_id=package_id, last_version=last_version,
                                                           project_name=project_name, current_version=current_version)
            app.db.session.add(user_package_table_data)
        else:
            item = app.PackageTable.query.filter(app.PackageTable.package_name == package_name).first()
            package_id = item.package_id
            last_version = item.last_version
            user_package_table_data = app.UserPackageTable(package_id=package_id, current_version=current_version,
                                                           last_version=last_version,
                                                           project_name=project_name)
            app.db.session.add(user_package_table_data)
    project_name_type_data = app.UserProjectTable(project_name=project_name, package_type=package_type)
    app.db.session.add(project_name_type_data)
    app.db.session.commit()


def add_package_to_project(project_name, package_type):
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
                                                       project_name=project_name)
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
                                                       project_name=project_name)
        app.db.session.add(user_package_table_data)
    app.db.session.commit()


def delete_package_from_project(project_name, package_id):
    project = app.UserPackageTable.query.filter_by(project_name=project_name, package_id=package_id).first()
    app.db.session.delete(project)
    app.db.session.commit()
