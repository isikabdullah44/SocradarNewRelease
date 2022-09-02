import json
import requests


def read_json(file_name, project_name):
    with open(f"uploads/{project_name}/{file_name}") as data_file:
        package_file = json.load(data_file)
    return package_file


def current_versions(file_name, project_name):
    package_file = read_json(file_name, project_name)
    current_versions_of_packages = {}
    package_of_headers = ['dependencies', 'devDependencies']
    for header in package_of_headers:
        for package_name in package_file[header]:
            current_package_version = package_file[header][package_name]
            disallowed_characters = "~^"
            for character in disallowed_characters:
                current_package_version = current_package_version.replace(character, "")
                current_versions_of_packages[package_name] = current_package_version

    return current_versions_of_packages


def node_package_search(package_name):
    response = requests.get(f'https://registry.npmjs.org/-/package/{package_name}/dist-tags')
    json_data = json.loads(response.text)
    last_version = json_data['latest']
    return last_version
