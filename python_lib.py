import json
import requests


def read_text(file_name, project_name):
    now_versions_of_packages = {}
    path = f"uploads/{project_name}/{file_name}"
    with open(path, 'r') as data_file:
        for line in data_file:
            data = line.split('==')
            package_name = data[0]
            package_version = data[1]
            final_package_version = package_version.replace("\n", "")
            now_versions_of_packages[package_name] = final_package_version

    return now_versions_of_packages


def current_versions(file_name, project_name):
    now_versions_of_packages = read_text(file_name, project_name)
    return now_versions_of_packages


def python_package_search(package_name):
    response = requests.get(f'https://pypi.org/pypi/{package_name}/json')
    json_data = json.loads(response.text)
    last_version = max(json_data['releases'])
    return last_version


def python_all_versions_of_packages(package_name):
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    json_data = json.loads(response.text)
    total_versions = []
    for versions in json_data['releases']:
        total_versions.append(versions)
    sorted_versions = sorted(total_versions)
    jsonStr = json.dumps(sorted_versions)
    return jsonStr
