#!/bin/sh -e
python setup.py test
easy_install sphinx
python setup.py build_sphinx sdist
