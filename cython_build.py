# pip install Cython==3.0.11

import os
import sys
import shutil
from setuptools import setup, find_packages
from Cython.Build import cythonize  # noqa


EXCLUDE_FILES = [
    "src/scripts/migrate_data_for_new_db.py"
]

NON_COMPILED_FILES = [
    "src/manage.py",
    "src/conf/gunicorn.conf.py"
]


def has_non_compilable_module(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    if content.find('pydantic') != -1:
        print('Using pydantic:', file_path)
        return True
    return False


def is_non_compilable_file(file_name, file_path):
    if file_path in NON_COMPILED_FILES:
        return True

    if has_non_compilable_module(file_path):
        return True

    if file_name[0].isdigit():
        # migration files
        return True

    return False


def is_ignored_file(file_name, file_path):
    # file_path: src/...
    if os.path.splitext(file_name)[1] != '.py':
        return True

    if file_path in EXCLUDE_FILES:
        return True

    if file_path.startswith('src/tests'):
        return True

    return False


def get_ext_paths(root_dir):
    """get filepaths for compilation"""
    paths = []
    non_compilable_paths = []
    for root, dirs, files in os.walk(root_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if is_ignored_file(file_name, file_path):
                continue

            if is_non_compilable_file(file_name, file_path):
                non_compilable_paths.append(file_path)
            else:
                paths.append(file_path)
    return paths, non_compilable_paths


def post_setup(non_compiled_paths, data_folders=None):
    for path in non_compiled_paths:
        # copy file src/... -> dist/app/...
        dest_path = path.replace('src/', 'dist/app/')
        try:
            shutil.copy(path, dest_path)  # noqa
            print('Copy {} to {}'.format(path, dest_path))
        except FileNotFoundError:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy(path, dest_path)  # noqa

    # data folders
    data_folders = data_folders or []
    for data_folder in data_folders:
        dest_path = data_folder.replace('src/', 'dist/app/')
        shutil.copytree(data_folder, dest_path, dirs_exist_ok=True)


def main():
    compiled_paths, non_compiled_paths = get_ext_paths('src')
    if sys.argv[1] == 'post-setup':
        post_setup(non_compiled_paths, data_folders=['src/apps/respond/resources/'])
        return

    setup(
        name='app',
        version='1.0',
        packages=find_packages(),
        ext_modules=cythonize(
            compiled_paths,
            compiler_directives={
                'language_level': 3,
                'annotation_typing': False,
                'always_allow_keywords': True
            },
        )
    )


main()
