from setuptools import setup, find_packages
import sys, os

from os.path import dirname, abspath
working_path = abspath(dirname(__file__))
sys.path.insert(0, working_path)

import versioneer

versioneer.versionfile_source = 'upstart/_version.py'
versioneer.versionfile_build = 'upstart/_version.py'
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'upstart-'

long_description=\
"An intuitive library interface to Upstart for service and job management. "\
"Requires the python-dbus Ubuntu package or equivalent."

setup(name='upstart',
      version=versioneer.get_version(),
      description="Upstart-based service management.",
      long_description=long_description,
      classifiers=[],
      keywords='upstart dbus',
      author='Dustin Oprea',
      author_email='myselfasunder@gmail.com',
      url='https://github.com/dsoprea/PythonUpstart',
      license='GPL 2',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[],
      entry_points="",
      cmdclass=versioneer.get_cmdclass(),
)

