import pynfdump
from pynfdump.nfdump import NFDumpError

from nose.tools import raises

@raises(NFDumpError)
def test_file_not_found():
    for x in pynfdump.search_file("this file isn't here"):
        print x

@raises(NFDumpError)
def test_bogus_options():
    for x in pynfdump.search_file("", statistics="foo", aggregate="bar"):
        print x
