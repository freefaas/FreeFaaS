# -*- coding: UTF-8 -*-

import boto3
import os
import requests
import zipfile
import StringIO
import time


def create_folder_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def download_zip_and_extractall_to_folder(url, folder):
    content = requests.get(url, stream=True).content
    archive = zipfile.ZipFile(StringIO.StringIO(content))
    archive.extractall(folder)


def fetch_lambda(name, target_folder):
    for i in range(3):
        try:
            response = client.get_function(FunctionName=name)
            # fetch config
            config_path = os.path.abspath(os.path.join(target_folder, 'config.dict'))
            config = response['Configuration']
            config_file = open(config_path, 'w+')
            config_file.write(str(config))
            config_file.flush()
            config_file.close()
            # fetch code
            code_path = os.path.abspath(os.path.join(target_folder, 'Code'))
            create_folder_if_not_exists(code_path)
            code = response['Code']
            repository_type = code['RepositoryType']
            location = code['Location']
            if repository_type == 'S3':
                download_zip_and_extractall_to_folder(location, code_path)
        except requests.exceptions.RequestException:
            t = 3 ** i
            print(str.format('{0} request error {1} times. Wait {2} seconds to restart.', name, i, t))
            time.sleep(3 ** i)
            continue
        break


# the output folder will be the git local working space
# delete the folder manually if necessary
output_folder = os.path.abspath(os.path.join('assets/aws/lambda'))
print(output_folder)

client = boto3.client('lambda')
functions = client.list_functions()['Functions']

for func in functions:
    functionName = func['FunctionName']
    # create function assets folder
    functionPath = os.path.abspath(os.path.join(output_folder, functionName))
    create_folder_if_not_exists(functionPath)
    print(functionPath)
    # dimensionality of versions
    versions = client.list_versions_by_function(FunctionName=functionName)['Versions']
    versionsPath = os.path.abspath(os.path.join(functionPath, 'versions'))
    create_folder_if_not_exists(versionsPath)
    for version in versions:
        versionArn = version['FunctionArn']
        # make version folder
        versionPath = os.path.abspath(os.path.join(versionsPath, version['Version']))
        print(versionPath)
        create_folder_if_not_exists(versionPath)
        fetch_lambda(versionArn, versionPath)
    # dimensionality of aliases
    aliases = client.list_aliases(FunctionName=functionName)['Aliases']
    aliasesPath = os.path.abspath(os.path.join(functionPath, 'aliases'))
    create_folder_if_not_exists(aliasesPath)
    for alias in aliases:
        aliasArn = alias['AliasArn']
        # make alias folder
        aliasPath = os.path.abspath(os.path.join(aliasesPath, alias['Name']))
        print(aliasPath)
        create_folder_if_not_exists(aliasPath)
        fetch_lambda(aliasArn, aliasPath)
