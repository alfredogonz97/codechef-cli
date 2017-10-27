# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from codecs import open
from sys import exit,version
import sys
if version < '2.0.0':
    print("Python 1 not supported...")
    sys.exit(1)

with open('README.md') as f:
    longd = f.read()

setup(
    name='codechefcli',
    include_package_data=True,
    packages=["codechefcli", "codechefcli.utils"],
    data_files=[('codechefcli', []), ('codechefcli.utils', [])],
    entry_points = {"console_scripts": ['codechefcli = codechefcli.__main__:main']},
    install_requires=['BeautifulSoup4','requests'],
    requires=['BeautifulSoup4','requests'],
    version='0.1',
    url='http://www.github.com/sk364/codechefcli',
    keywords="codechef cli",
    license='GNU',
    author='Sachin Kukreja',
    author_email='skad5455@gmail.com',
    description='CodeChef command line interface. CodeChefCLI helps competitive coders to view, submit, comment on problems in CodeChef',
    long_description="\n\n"+longd
)