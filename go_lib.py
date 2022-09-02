import json
import requests
import os

path = "/Users/pexatv/Desktop/SocradarNewRelease/uploads"
dir_list = os.listdir(path)


def read_file(file_name, project_name):
    current_versions_of_packages = {}
    data = []
    x = 0
    with open(f"uploads/{project_name}/{file_name}") as data_file:
        for line in data_file:
            line = line.split(' ')
            data.append(line)
        while True:
            if len(data[x]) > 2:
                package_name = data[x][1]
                package_version = data[x][2]
                current_versions_of_packages[package_name] = package_version
                x += 1
            elif x < len(data) - 1:
                x += 1

            else:
                break

    return current_versions_of_packages


def current_versions(file_name, project_name):
    current_versions_of_packages = read_file(file_name, project_name)
    return current_versions_of_packages


def go_package_search(package_name):
    response = requests.get(f"https://proxy.golang.org/{package_name}/@latest")
    json_data = json.loads(response.text)
    last_version = json_data['Version']
    return last_version


