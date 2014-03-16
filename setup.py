from setuptools import setup, find_packages
import sys, os

from distutils.dist import Distribution


print("MODULE: %s" % (__name__))


import termios, sys, os
 
def read_keys():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
    new[6][termios.VMIN] = 1
    new[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, new)
    try:
        while 1:
            yield os.read(fd, 1)
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, old)


class VersionedDistribution(Distribution):
      """We set the versioneer components once the flow actually begins, and 
      all of the modules are in place.
      """

      def __init__(self, attrs):
            import time
            import os

            print("CWD: %s" % (os.getcwd()))

            print("Press key.")
            read_keys().next()

            import versioneer

            versioneer.versionfile_source = 'upstart/_version.py'
            versioneer.versionfile_build = 'upstart/_version.py'
            versioneer.tag_prefix = ''
            versioneer.parentdir_prefix = 'upstart-'

            attrs['version'] = versioneer.get_version()
            attrs['cmdclass'] = versioneer.get_cmdclass()

            Distribution.__init__(self, attrs)

long_description=\
"An intuitive library interface to Upstart for service and job management. "\
"Requires the python-dbus Ubuntu package or equivalent."

setup(distclass=VersionedDistribution,
      name='upstart',
      version=None, #_VLazyVersion(), #versioneer.get_version(),
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
      cmdclass=None,#versioneer.get_cmdclass(),
#      cmdclass=_VLazyCmdClass()
)
