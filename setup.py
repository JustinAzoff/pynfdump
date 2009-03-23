from setuptools import setup, find_packages
import sys, os
from glob import glob

version = '0.3'

setup(name='pynfdump',
    version=version,
    description="python interface to nfdump",
    long_description="""\
pynfdump is a frontend to the nfdump CLI app
It supports normal, aggregation, and statistics modes.
It supports running nfdump on a remote host via ssh.
""",
    classifiers=[
        "Topic :: System :: Networking",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
    ],
    keywords='nfdump netflow',
    author='Justin Azoff',
    author_email='JAzoff@uamail.albany.edu',
    url='http://packages.python.org/pynfdump',
    download_url="http://github.com/JustinAzoff/pynfdump/tree/master",
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        "dateutil",
        "IPy",
    ],
    scripts=glob('scripts/*'),
    test_suite='nose.collector',
    )
