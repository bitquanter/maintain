#!/usr/bin/env python
# coding:utf-8

from __future__ import print_function


import os
import sys
import zipfile
import glob
from os.path import dirname, join
#from pip.req import parse_requirements

from setuptools import (
    find_packages,
    setup,
)
# from Cython.Build import cythonize


def zip_dir(zip_path, dir):
    zip_path = os.path.abspath(zip_path)
    cwd = os.path.abspath(os.getcwd())
    os.chdir(dir)
    ziph = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    # ziph is zipfile handle
    for root, dirs, files in os.walk('.'):
        for file in files:
            ziph.write(os.path.join(root, file))
    ziph.close()
    os.chdir(cwd)


def unzip_to_dir(zip_path, target_dir):
    import zipfile
    zip_ref = zipfile.ZipFile(zip_path, 'r')
    zip_ref.extractall(target_dir)
    zip_ref.close()


def remove_py_file_from_egg():
    def remove(path):
        if os.path.exists(path):
            print("removing {} from egg".format(path))
            os.remove(path)

    import glob
    import tempfile
    import shutil
    eggs = glob.glob('dist/*.egg')
    if eggs:
        for egg in eggs:
            tmpdir = tempfile.mkdtemp()
            unzip_to_dir(egg, tmpdir)
            for file in encrypt_files:
                remove(tmpdir + '/' + file)
                remove(tmpdir + '/' + file.replace('.py', '.c'))
                remove(tmpdir + '/' + file.replace('.py', '.pyc'))
                remove(tmpdir + '/' + file.replace('.py', '.pyo'))
            zip_dir(egg, tmpdir)
            shutil.rmtree(tmpdir)
    pass


def get_encrypt_files(pattens):
    files = []
    for patten in pattens:
        files += glob.glob(patten)
    files = [f for f in files if '__init__' not in f]
    return files


if '--encrypt' in sys.argv or 'build_ext' in sys.argv:
    if '--encrypt' in sys.argv:
        sys.argv.remove('--encrypt')
    encrypt_files = get_encrypt_files([
        'bpdata/*.py',
    ])
    from Cython.Build import cythonize
    ext_modules = cythonize(encrypt_files)
else:
    encrypt_files = []
    ext_modules = []

CURDIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(CURDIR, 'VERSION.txt'), 'rb') as f:
    version = f.read().decode('ascii').strip()

#requirements = [str(ir.req) for ir in parse_requirements("requirements.txt", session=False)]

setup(
    name='bpdata',
    version=version,
    description='bitup data package',
    packages=find_packages(exclude=['tests', 'tests.*']),
    ext_modules=ext_modules,
    # packages=['bpdata'],
    author='zhengdalong',
    author_email='zdl@bitup.com',
    package_data={'': ['*.*']},
    include_package_data=True,

    url='https://www.bitup.com',
    #install_requires=requirements,
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

if 'bdist_egg' in sys.argv:
    remove_py_file_from_egg()
