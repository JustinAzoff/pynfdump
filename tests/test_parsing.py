import pynfdump

def parse_search_helper(txt):
    lines = [l.strip() for l in txt.strip().splitlines()]
    return list(pynfdump.Dumper().parse_search(lines))

def parse_stats(txt):
    lines = [l.strip() for l in txt.strip().splitlines()]
    return list(pynfdump.Dumper().parse_stats(lines))

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
