#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path

from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop

here = path.abspath(path.dirname(__file__))
README = open(path.join(here, 'README')).read()
CHANGES = open(path.join(here, 'CHANGES.txt')).read()
CONFIG_FILE = path.join(here, 'config.ini')
requires = [
  'ConfigParser', 
  'python-dateutil', 
  'Scrapy',
  'selenium',
  'service_identity',
  'SQLAlchemy'
]

# Taken from:
# http://www.niteoweb.com/blog/setuptools-run-custom-code-during-install
def config_file(command_subclass):
  """A decorator for classes subclassing one of the setuptools commands.

  It modifies the run() method so that it prints a friendly greeting.
  """
  orig_run = command_subclass.run

  def modified_run(self):
    import ConfigParser
    config = ConfigParser.ConfigParser()
    with open(CONFIG_FILE) as fp:
      config.readfp(fp)
    config.set('project', 'base_dir', here)
    config.set('project', 'binaries', here + '/bin')
    config.set('project', 'db', here + '/data')
    config.set('project', 'pictures', here + '/data/pictures')
    config.set('project', 'documentation', here + '/doc')
    config.set('project', 'source_code', here + '/facebook-friends')
    config.set('db', 'url', 'sqlite:///{0}/{1}'\
      .format(here + '/data', config.get('db', 'name')))
    with open(CONFIG_FILE, 'wb') as configfile:
      config.write(configfile)
    orig_run(self)
  
  command_subclass.run = modified_run
  return command_subclass

@config_file
class CustomDevelopCommand(develop):
  pass

@config_file
class CustomInstallCommand(install):
  pass

setup(name='facebook-friends', 
  version='0.1', 
  description='Facebook friend scrapper',
  long_description=README + '\n\n' +  CHANGES,
  classifiers=[
    "Programming Language :: Python",
    "Topic :: Database :: Database Engines/Servers",
    "Topic :: Internet :: WWW/HTTP :: Indexing/Search"
  ],
  author='Nestor Bohorquez',
  author_email='tca7410nb@gmail.com',
  url='https://nbohorquez.github.io/',
  keywords='facebook friends spider',
  packages=find_packages(),
  include_package_data=True,
  zip_safe=False,
  test_suite='facebook-friends',
  install_requires=requires,
  cmdclass={
    'install': CustomInstallCommand,
    'develop': CustomDevelopCommand
  },
  entry_points={
    'console_scripts': [
      'load_constants = facebook-friends.scripts.load_constants:main',
      'scrap = facebook-friends.scripts.scrap:main'
    ],
    'scrapy': ['settings = facebook-friends.settings']
  }
)
