# -*- coding: UTF-8 -*-

import boto3
import os
import requests
import zipfile
import StringIO


def create_folder_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def download_zip_and_extractall_to_folder(url, folder):
    content = requests.get(url, stream=True).content
    archive = zipfile.ZipFile(StringIO.StringIO(content))
    archive.extractall(folder)
    print


def fetch_lambda(name, target_folder):
    response = client.get_function(FunctionName=name)

    config = response['Configuration']
    config_path = os.path.abspath(os.path.join(target_folder, 'config.dict'))
    # save configuration to file
    config_file = open(config_path, 'w+')
    config_file.write(str(config))
    config_file.flush()
    config_file.close()

    code_path = os.path.abspath(os.path.join(target_folder, 'Code'))
    create_folder_if_not_exists(code_path)
    # save code to files
    code = response['Code']
    repository_type = code['RepositoryType']
    location = code['Location']

    if repository_type == 'S3':
        download_zip_and_extractall_to_folder(location, code_path)


# the output folder will be the git local working space
# delete the folder manually if necessary
output_folder = os.path.abspath(os.path.join('../../assets'))
print output_folder

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
        print versionPath
        create_folder_if_not_exists(versionPath)
        fetch_lambda(versionArn, versionPath)
        # may be useful in future
        # tags = response['Tags']
        # concurrency = response['Concurrency']
    # dimensionality of aliases
    aliases = client.list_aliases(FunctionName=functionName)['Aliases']
    aliasesPath = os.path.abspath(os.path.join(functionPath, 'Aliases'))
    create_folder_if_not_exists(aliasesPath)
    for alias in aliases:
        aliasArn = alias['AliasArn']
        # make alias folder
        aliasPath = os.path.abspath(os.path.join(aliasesPath, alias['Name']))
        print aliasPath
        create_folder_if_not_exists(aliasPath)
        fetch_lambda(aliasArn, aliasPath)
    # may be useful in future
    # response = client.list_event_source_mappings(FunctionName=functionName)
    # print(response)
