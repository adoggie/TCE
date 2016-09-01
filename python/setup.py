
# python setup.py bdist_egg

from setuptools import setup,find_packages

setup(
	name='tcelib',
	version='0.1.0',
	packages = find_packages(),
	# zip_safe = False,
	description='tce for python',
	# long_description='tiny communication engine',
	author='scott',
	author_email='socketref@hotmail.com',
	# keywords=('tce','rpc'),
	# platforms='Independant',
	url='',
	install_requires = ['gevent'],

)
