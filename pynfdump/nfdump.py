# nfdump.py
# Copyright (C) 2008 Justin Azoff JAzoff@uamail.albany.edu
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php
"""
Python frontend to the nfdump CLI
"""

import os
from dateutil.parser import parse as parse_date
import datetime.datetime
fromtimestamp = datetime.datetime.fromtimestamp

from subprocess import Popen, PIPE
import commands

from IPy import IP

FILE_FMT = "%Y %m %d %H %M".replace(" ","")

def date_to_fn(date):
    return 'nfcapd.' + date.strftime(FILE_FMT)

def run(cmds):
    #print ' '.join(cmds)
    output = Popen(cmds, stdout=PIPE,stderr=PIPE).communicate()
    return output

def maybe_int(val):
    try:
        val = int(val)
    except TypeError:
        pass
    except ValueError:
        pass
    return val

class NFDumpError(Exception):
    pass

class Dumper:
    def __init__(self, datadir, profile='live',sources=None,remote_host=None):
        if not datadir.endswith("/"):
            datadir = datadir + '/'
        self.datadir = datadir
        self.profile = profile
        self.sources = sources
        self.remote_host = remote_host
        self.set_where()

    def set_where(self, start=None, end=None):
        """Set the timeframe of the nfdump query
           Specify just the start date or both the start and end date
        """
        
        self.start = start
        self.end = end

        self.sd = self.ed = None

        if start:
            self.sd = parse_date(start)
        if end:
            self.ed = parse_date(end)

        if not self.sd:
            self._where = '.'
        else:
            self._where = date_to_fn(self.sd)
            if self.ed:
                self._where += ":" + date_to_fn(self.ed)

    def make_query(self, q):
        if self.remote_host:
            return commands.mkarg(q)
        else:
            return q

    def search(self, query, aggregate=None, statistics=None, statistics_order=None,limit=None):
        """Run nfdump with the following arguments:
            * aggregate: (True OR comma sep string OR list) of 'srcip dstip srcport dstport'
            * statistics Generate netflow statistics info
            * statistics_order: one of srcip, dstip, ip, srcport, dstport, port
                                       srcas, dstas, as, inif , outif, proto
            * limit number of results
        """

        sources = ':'.join(self.sources)
        d = os.path.join(self.datadir, self.profile, sources)

        cmd = []
        if self.remote_host:
            cmd = ['ssh', self.remote_host]

        cmd.extend(['nfdump', '-o','pipe', '-M', d, '-R', self._where, self.make_query(query)])


        if aggregate and statistics:
            raise NFDumpError("Specify only one of aggregate and statistics")

        if statistics:
            s_arg = statistics
            if statistics_order:
                s_arg = "%s/%s" % (statistics, statistics_order)

            cmd.extend(["-s", s_arg])

        if aggregate:
            if aggregate is True:
                cmd.append("-a")
            else:
                if ',' not in aggregate:
                    aggregate = ','.join(aggregate)
                cmd.extend(["-a", "-A", aggregate])

        if limit:
            if statistics:
                cmd.extend(['-n',str(limit)])
            else:
                cmd.extend(['-c',str(limit)])

        out,err = run(cmd)
        out = out.splitlines()
        if err:
            raise NFDumpError(err)
        if statistics:
            return self.parse_stats(out, object_field=statistics)
        else:
            return self.parse_search(out)

    def parse_search(self, out):
        for line in out:
            parts = line.split("|")
            parts = [maybe_int(x) for x in parts]
            if not len(parts) > 20:
                continue
            row = {
                'af':           parts[0],
                'first':        fromtimestamp(parts[1]),
                #'msec_first':   parts[2],
                'last':         fromtimestamp(parts[3]),
                #'msec_last':    parts[4],
                'prot':         parts[5],
                #'sa0':          parts[6],
                #'sa1':          parts[7],
                #'sa2':          parts[8],
                'src':          IP(parts[9]),
                'srcport':      parts[10],
                #'da0':          parts[11],
                #'da1':          parts[12],
                #'da2':          parts[13],
                'dst':          IP(parts[14]),
                'dstport':      parts[15],
                'srcas':        parts[16],
                'dstas':        parts[17],
                'input':        parts[18],
                'output':       parts[19],
                'flags':        parts[20],
                'tos':          parts[21],
                'packets':      parts[22],
                'bytes':        parts[23],
            }
            yield row

    def parse_stats(self, out,object_field):
        for line in out:
            parts = line.split("|")
            parts = [maybe_int(x) for x in parts]
            if not len(parts) > 10:
                #print line
                continue
            if '0|0|0|0' in line:
                object_idx = 9
            else:
                object_idx = 6
            row = {
                'af':           parts[0],
                'first':        fromtimestamp(parts[1]),
                #'msec_first':   parts[2],
                'last':         fromtimestamp(parts[3]),
                #'msec_last':    parts[4],
                'prot':         parts[5],
                object_field:   parts[object_idx],
                'flows':        parts[object_idx+1],
                'packets':      parts[object_idx+2],
                'bytes':        parts[object_idx+3],
                'pps':          parts[object_idx+4],
                'bps':          parts[object_idx+5],
                'bpp':          parts[object_idx+6],
            }

            if 'ip' in object_field:
                row[object_field] = IP(row[object_field])

            yield row


    def list_profiles(self):
        """Return a list of the nfsen profiles"""
        if not self.remote_host:
            return os.listdir(self.datadir)
        else:
            return run(['ssh', self.remote_host, '/bin/ls', self.datadir])[0].split()

    def get_profile_data(self, profile=None):
        """Return a dictionary of the nfsen profile data"""
        p = profile or self.profile
    
        path = os.path.join(self.datadir,p,'profile.dat')
    
        if not self.remote_host:
            data = open(path).read()
        else:
            data = run(['ssh', self.remote_host, '/bin/cat', path])[0]

        ret = {}
        for line in data.splitlines():
            if not line: continue
            if line[0] in ' #': continue
            key, val = line.split(" = ", 1)
            if key == 'sourcelist':
                val = val.split(":")

            ret[key] = maybe_int(val)
        return ret
