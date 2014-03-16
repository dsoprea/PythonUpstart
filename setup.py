from setuptools import setup, find_packages
import sys, os


long_description=\
"An intuitive library interface to Upstart for service and job management. "\
"Requires the python-dbus Ubuntu package or equivalent."

setup(name='upstart',
      version='0.3.1',#versioneer.get_version(),
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
      scripts=['scripts/upstart-create',
               'scripts/upstart-reload'],
#      cmdclass=versioneer.get_cmdclass(),
)
