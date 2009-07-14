#!/bin/sh -e
python setup.py test
python setup.py build_sphinx sdist
