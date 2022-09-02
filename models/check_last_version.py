import app
import go_lib
import node_lib
import python_lib

datas = app.PackageTable.query.all()
for data in datas:
    package_name = data.package_name
    last_version_on_data = data.last_version
    package_type = data.package_type
    apps = {
        "node": node_lib.node_package_search,
        "python": python_lib.python_package_search,
        "go": go_lib.go_package_search

    }
    current_last_version = apps[package_type](package_name)
    if not last_version_on_data == current_last_version:
        data.last_version = current_last_version
        app.db.session.commit()
