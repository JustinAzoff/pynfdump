from setuptools import setup, find_packages
import sys, os
from glob import glob

version = '0.1'

setup(name='pynfdump',
      version=version,
      description="python interface to nfdump",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='nfdump netflow',
      author='Justin Azoff',
      author_email='JAzoff@uamail.albany.edu',
      url='',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        "dateutil"
      ],
      scripts=glob('scripts/*'),
      )
