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
import datetime
fromtimestamp = datetime.datetime.fromtimestamp

from subprocess import Popen, PIPE
import commands

from IPy import IP

FILE_FMT = "%Y %m %d %H %M".replace(" ","")

def load_protocols():
    #2.4 doesn't have socket.getprotocol by id
    f = open("/etc/protocols")
    protocols = {}
    for line in f:
        if not line.strip():
            break
    for line in f:
        if not line.strip(): break
        proto, num,_ = line.split(None,2)
        protocols[int(num)] = proto
    protocols[0]='ip'
    f.close()
    return protocols

def date_to_fn(date):
    return 'nfcapd.' + date.strftime(FILE_FMT)

def run(cmds):
    #print (cmds)
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
    def __init__(self, datadir='/', profile='live',sources=None,remote_host=None):
        if not datadir.endswith("/"):
            datadir = datadir + '/'
        self.datadir = datadir
        self.profile = profile
        self.sources = sources
        self.remote_host = remote_host
        self.set_where()
        self.protocols = load_protocols()

    def set_where(self, start=None, end=None, filename=None,dirfiles=None, stdin=False):
        """Set the timeframe of the nfdump query.
        Specify one of the following:

            * The start date
            * The start and end date
            * one of the filename,dirfiles, or stdin options

        :param start: Start date and time
        :param end: Start date and time
        :param filename: Search this single filename
        :param dirfiles: Search this directory
        :param stdin:    Search stdin
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

        if dirfiles:
            self._where = dirfiles

        self.filename = filename
        if stdin:
            self.filename = '-'

    def _arg_escape(self, arg):
        """Escape any arguments so that they can be passed over SSH"""
        if self.remote_host:
            return commands.mkarg(arg)
        else:
            return arg

    def search(self, query='', aggregate=None, statistics=None, statistics_order=None,limit=None):
        """Run nfdump with the following arguments

        :param query: The nfdump filter
        :param aggregate: (True OR comma sep string OR list) of

            * srcip     - Source IP Address
            * dstip     - Destination IP Address
            * srcport   - Source Port
            * dstport   - Destination Port

        :param statistics: Generate netflow statistics info, one of

            * srcip     - Source IP Address
            * dstip     - Destination IP Address
            * ip        - Any IP Address
            * srcport   - Source Port
            * dstport   - Destination Port
            * port      - Any Port
            * srcas     - Source ASN
            * dstas     - Destination ASN
            * as        - Any ASN
            * inif      - Incoming Interface
            * outif     - Outgoing Interface
            * proto     - Protocol

        :param statistics_order: one of

            * packets
            * bytes
            * flows
            * bps       - Bytes Per Second
            * pps       - Packers Per Second
            * bpp.      - Bytes Per Packet

        :param limit: number of results
        """

        cmd = []
        if self.remote_host:
            cmd = ['ssh', self.remote_host]
        cmd.extend(['nfdump', '-q', '-o', 'pipe', self._arg_escape(query)])

        if self.filename:
            cmd.extend(['-r', self.filename])
        else:
            if self.datadir and self.sources and self.profile:
                sources = ':'.join(self.sources)
                d = os.path.join(self.datadir, self.profile, sources)
                cmd.extend(['-M', d])
            cmd.extend(['-R', self._where])


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
                aggregate = aggregate.replace(" ","")
                cmd.extend(["-a", "-A", self._arg_escape(aggregate)])

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
        #    snprintf(data_string, STRINGSIZE-1 ,"%i|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%u|%llu|%llu",
        #                0 af, 1 r->first, 2 r->msec_first ,3 r->last, 4 r->msec_last, 5 r->prot,
        #                6 sa[0], 7 sa[1], 8 sa[2], 9 sa[3], 10 r->srcport, 11 da[0], 12 da[1], 13 da[2], 14 da[3], 15 r->dstport,
        #                16 r->srcas, 17 r->dstas, 18 r->input, 19 r->output,
        #                20 r->tcp_flags, 21 r->tos, 22 (unsigned long long)r->dPkts, 23 (unsigned long long)r->dOctets);

        for line in out:
            parts = line.split("|")
            parts = [int(x) for x in parts]
            if not len(parts) > 20:
                continue
            row = {
                'af':           parts[0],
                'first':        fromtimestamp(parts[1]),
                #'msec_first':   parts[2],
                'last':         fromtimestamp(parts[3]),
                #'msec_last':    parts[4],
                'prot':         self.protocols.get(parts[5]),
                #'sa0':          parts[6],
                #'sa1':          parts[7],
                #'sa2':          parts[8],
                'srcip':        IP(parts[9]),
                'srcport':      parts[10],
                #'da0':          parts[11],
                #'da1':          parts[12],
                #'da2':          parts[13],
                'dstip':          IP(parts[14]),
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
                'prot':         self.protocols.get(parts[5]),
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
        sourcelist = []
        for line in data.splitlines():
            if not line: continue
            if line[0] in ' #': continue
            key, val = line.split(" = ", 1)
            if key == 'channel':
                chan = val.split(":")[0]
                sourcelist.append(chan)
                continue

            ret[key] = maybe_int(val)
        if sourcelist:
            ret['sourcelist'] = sourcelist
        return ret

def search_file(filename, query='', aggregate=None, statistics=None, statistics_order=None,limit=None):
    """Search a single nfcapd file

    :param filename: the file to search

    The rest of the options are passed directly to :func:`Dumper.search`
    """

    d = Dumper()
    d.set_where(filename=filename)
    return d.search(query, aggregate, statistics, statistics_order, limit)
