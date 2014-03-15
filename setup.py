from setuptools import setup, find_packages
import sys, os


class _VLazy(object):
      """The lazy logic for Versioneer. We can't determine any version stuff 
      when this file is first loaded because none of the other modules may yet 
      be in place (when installing via PIP, for instance).
      """

      def __init__(self):
            self.__versioneer = None

      def __init_versioneer(self):
            if self.__versioneer is None:
                  import versioneer

                  versioneer.versionfile_source = 'upstart/_version.py'
                  versioneer.versionfile_build = 'upstart/_version.py'
                  versioneer.tag_prefix = ''
                  versioneer.parentdir_prefix = 'upstart-'

                  self.__versioneer = versioneer

      def get_version(self):
            self.__init_versioneer()
            return self.__versioneer.get_version()

      def get_cmdclass(self):
            self.__init_versioneer()
            return self.__versioneer.get_cmdclass()


class _VLazyVersion(str):
      """Wait to determine the version until someone actually casts us or 
      applies us, after our whole project has been staged.
      """

      def __init__(self, v):
            super(_VLazyVersion, self).__init__()

            self.__v = v
            self.__is_loaded = False

      def __repr__(self):
            return str(self)

      def __str__(self):
            if self.__is_loaded is False:
                  self.__version = self.__v.get_version()
                  self.__is_loaded = True

            return self.__version

class _VLazyCmdClass(dict):
      """Wait to determine the cmdclass until someone actually requests a 
      particular class, at which point we proxy the request to the actual 
      dictionary.
      """

      def __init__(self, v):
            super(_VLazyCmdClass, self).__init__()

            self.__v = v
            self.__is_loaded = False

      def __attr__(self, name):
            """Proxy all requests through to the standard dictionary object. 
            The first time we're called, load ourselves with the Versioneer 
            cmdclass entries.
            """

            if self.__is_loaded is False:
                  self.update(self.__v.get_cmdclass())
                  self.__is_loaded = True

            return getattr(self, name)

long_description=\
"An intuitive library interface to Upstart for service and job management. "\
"Requires the python-dbus Ubuntu package or equivalent."

v = _VLazy()

setup(name='upstart',
      version=_VLazyVersion(v), #versioneer.get_version(),
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
      cmdclass=_VLazyCmdClass(v)
#      cmdclass=versioneer.get_cmdclass(),
)
