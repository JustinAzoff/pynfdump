import pynfdump

def parse_search_helper(txt):
    lines = [l.strip() for l in txt.strip().splitlines()]
    return list(pynfdump.Dumper().parse_search(lines))

def parse_stats(txt):
    lines = [l.strip() for l in txt.strip().splitlines()]
    return list(pynfdump.Dumper().parse_stats(lines))

def parse_flow_stats(txt):
    lines = [l.strip() for l in txt.strip().splitlines()]
    return pynfdump.Dumper().parse_flow_stats(lines)

def test_parse_1():
    out = """
    2|1235500152|664|1235500152|676|6|0|0|0|1234567890|1672|0|0|0|1122112211|80|0|0|5|7|17|0|2|80
    2|1235500152|664|1235500152|844|6|0|0|0|1234567890|1729|0|0|0|1321321321|80|0|0|5|7|27|0|6|2640
    2|1235500152|668|1235500153|32|6|0|0|0|1231231231|80|0|0|0|1234567890|1726|0|0|7|5|27|0|7|5774
    """

    expected = [
        {'srcip': '73.150.2.210', 'dstip': '66.226.18.211' },
        {'srcip': '73.150.2.210', 'dstip': '78.193.195.105', },
        {'srcip': '73.99.24.255', 'dstip': '73.150.2.210',  },
    ]

    for a,b in zip(parse_search_helper(out), expected):
        for k,v in b.items():
            msg =  "field:%s expected:%s actual:%s" % (k, v, a[k])
            assert str(a[k]) == v, msg

def test_parse_flow_stats():
    output=  """Ident: podium
                Flows: 1722928
                Flows_tcp: 977659
                Flows_udp: 558117
                Flows_icmp: 186290
                Flows_other: 862
                Packets: 47666242
                Packets_tcp: 43564336
                Packets_udp: 3630117
                Packets_icmp: 287842
                Packets_other: 183947
                Bytes: 39292717725
                Bytes_tcp: 37649407665
                Bytes_udp: 1476970116
                Bytes_icmp: 101758614
                Bytes_other: 64581330
                First: 1350232199
                Last: 1350235497
                msec_first: 249
                msec_last: 655
                Sequence failures: 0
                """
    stats = parse_flow_stats(output)
    assert stats['msec_first'] == 249
    assert stats['bytes'] == 39292717725
    assert stats['ident'] == "podium"

from pynfdump.nfdump import maybe_split
def test_maybe_split():
    assert ["hello"] == maybe_split("hello",",")
    assert ["hello"] == maybe_split(["hello"],",")

    assert ["a","b"] == maybe_split(["a","b"], ",")
    assert ["a","b"] == maybe_split("a,b", ",")
