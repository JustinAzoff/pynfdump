Usage
=====

The two main user facing functions of the Dumper class are
:func:`pynfdump.nfdump.Dumper.set_where` which sets the time frame of the search, and 
:func:`pynfdump.nfdump.Dumper.search` which does the actual searching.

Basic search
------------

Lets search for any traffic going to a single IP address:::

    >>> ip=socket.gethostbyname("bouncybouncy.net")
    >>> d=pynfdump.Dumper("/data/nfsen/profiles",sources=['podium'],remote_host='glenn')
    >>> d.set_where(start="2009-03-23 11:00")
    >>> records=d.search("dst ip %s" % ip)
    >>> for r in records:
    ...     print r['last'], r['dstip'], r['dstport'], r['bytes']
    ... 
    2009-03-23 11:49:48 74.70.148.119 5222 205
    2009-03-23 11:50:17 74.70.148.119 5222 205
    2009-03-23 11:50:49 74.70.148.119 5222 361
    2009-03-23 11:54:16 74.70.148.119 5222 1230
    2009-03-23 11:55:16 74.70.148.119 5222 410
    2009-03-23 11:55:46 74.70.148.119 5222 205
    2009-03-23 11:59:47 74.70.148.119 5222 1640

This found a number of flows going to my jabber server.


Aggregates
------------

Lets repeat the previous search, but have nfdump aggregate the records for us::

    >>> records=d.search("dst ip %s" % ip, aggregate='dstip, dstport')
    >>> for r in records:
    ...     print r['last'], r['dstip'], r['dstport'], r['bytes']
    ... 
    2009-03-23 12:14:16 74.70.148.119 5222 9895

:func:`pynfdump.nfdump.Dumper.search` also accepts a iterable for the aggregate
option, so the following works as well::

    >>> records=d.search("dst ip %s" % ip, aggregate=['dstip','dstport'])


Statistics
------------

pynfdump supports the statistics modes of nfdump.  This example will show the
top three ports ordered by bytes::

    >>> for r in d.search('', statistics='port', statistics_order='bytes',limit=3):
    ...     print r['port'], r['bytes']
    80 25066905131
    388 5247458707
    1935 2466061151



Profile inspection
------------------

You can list profiles, and get information about profiles::

    >>> d.list_profiles()
    ['live', ...]

    >>> import pprint
    >>> pprint.pprint(d.get_profile_data("live"))
    {'expire': 0,
     'group': '.',
     'locked': 0,
     'maxsize': 45097156608L,
     'name': 'live',
     'size': 40675028992L,
     'sourcelist': ['resnet', 'span', 'podium'],
     'status': 'OK',
     'tbegin': 0,
     'tcreate': 0,
     'tend': 1237825800,
     'tstart': 1235390700,
     'type': 0,
     'updated': 1237825800,
     'version': 130}
