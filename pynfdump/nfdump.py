import os
from mx.DateTime import DateTimeFrom as parse_date, DateTimeFromTicks
from subprocess import Popen, PIPE

from IPy import IP

FILE_FMT = "%Y %m %d %H %M".replace(" ","")

def run(cmds):
    output = Popen(cmds, stdout=PIPE).communicate()[0]
    return output

class Dumper:
    def __init__(self, datadir, profile='live',sources=None):
        if not datadir.endswith("/"):
            datadir = datadir + '/'
        self.datadir = datadir
        self.profile = profile
        self.sources = sources

    def set_where(self, start=None, end=None):
        self.start = start
        self.end = end

        self.sd = self.ed = None

        if start:
            self.sd = parse_date(start)
        if end:
            self.ed = parse_date(end)

    def search(self, query, args=None, aggregate=None, statistics=None, statistics_order=None):
        sources = ':'.join(self.sources)
        d = os.path.join(self.datadir, self.profile, sources)
        cmd = ['nfdump', '-o','pipe', '-M', d, '-R', '.', query]


        if aggregate and statistics:
            raise RuntimeError("Specify only one of aggregate and statistics")

        if statistics:
            if statistics_order:
                statistics = "%s/%s" % (statistics, statistics_order)
            cmd.extend(["-s", statistics])

        if aggregate:
            if aggregate is True:
                cmd.append("-a")
            else:
                cmd.extend(["-a", "-A", aggregate])

        out = run(cmd)
        if statistics:
            return self.parse_stats(out)
        else:
            return self.parse_search(out)

    def parse_search(self, out):
        for line in out.splitlines():
            parts = line.split("|")
            if not len(parts) > 20:
                continue
            row = {
                'af':           parts[0],
                'first':        DateTimeFromTicks(parts[1]),
                #'msec_first':   parts[2],
                'last':         DateTimeFromTicks(parts[3]),
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
                'octects':      parts[23],
            }
            yield row

    def parse_stats(self, out):
        for line in out.splitlines():
            parts = line.split("|")
            if not len(parts) > 10:
                print line
                continue
            row = {
                'af':           parts[0],
                'first':        DateTimeFromTicks(parts[1]),
                #'msec_first':   parts[2],
                'last':         DateTimeFromTicks(parts[3]),
                #'msec_last':    parts[4],
                'prot':         parts[5],
                'object':       IP(parts[6]),
                'flows':        parts[7],
                'packets':      IP(parts[8]),
                'bytes':        parts[9],
                'pps':          parts[10],
                'bps':          parts[11],
                'bpp':          parts[12],
            }
            yield row
