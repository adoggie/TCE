#coding:utf-8

from setuptools import setup, find_packages

setup(
        name = 'tmake',
        version = '1.0.5',
        packages = find_packages(),
        author = 'scott',
        author_email = 'socketref@hotmail.com',
        url = 'http://github.com/adoggie/TCE',
        license = 'http://www.apache.org/licenses/LICENSE-2.0.html',
        description = 'TCE',
        package_data ={ '':[]},
        install_requires = ['ply'],

        )