from logging import (getLogger, basicConfig)
from sys import argv
from typing import Set

basicConfig(format='[%(asctime)s - %(levelname)s] %(message)s',
            datefmt="%H:%M:%S")
logger = getLogger("DoS_test")
logger.setLevel("INFO")

class Methods:
    LAYER7_METHODS: Set[str] = {"get", "post", "pps", "ovh",
                                "avb", "cfb", "bot", "gsb",
                                "dyn", "rhex", "slow", "dgb",
                                "null", "stomp", "stress", "cfbuam",
                                "xmlrpc", "apache", "bypass", "killer",
                                "cookie", "downloader"
                                }

    LAYER4_METHODS: Set[str] = {"tcp", "udp", "syn", "icmp",
                                "dns", "gre", "dns_ampl"
                                }

class ToolsConsole:
    @staticmethod
    def usage():
        print((
                '* DoS_test - DoS/DDoS скрипт, поддерживающий %d веткоров атак\n'
                'Note: Вся конфигурация стенда и атаки указывается в конфиге(platform_config.json)\n'
                '    При запуске скрипта указывается только полный путь до конфига через ключ "-c"\n'
                ' > Поддерживаемые векторы атак:\n'
                ' - L4:\n'
                ' | %s | %d Методов\n'
                ' - L7:\n'
                ' | %s | %d Метода\n'
                '\n'
                'Методы:\n'
                ' - L4: \n'
                '      tcp:   Подключение к серверу и флуд tcp пакетами c рандомным payload, размером 1024 байта\n'
                '      udp:   Подключение к серверу и флуд udp пакетами c рандомным payload, размером 1024 байта\n'
                '      syn:   Флуд syn пакетами на целевой адрес, src port рандомный(32768 - 65535)\n'
                '      dns:   Флуд DNS запросами на целевой адрес\n'
                '      cps:   Connect на целевой сервер без дальнейшего поддержания соединения\n'
                '      icmp:  Флуд ICMP пакетами на целевой адрес\n'
                '      fivem: Fivem Status Ping\n'
                '      connection: Connect на целевой сервер с дальнейшим поддержанием соединения\n'
                ' - L7: \n'
                '      get:   Подключение к серверу и флуд get запросами\n'
                '      pps:   Подключение к серверу и флуд "GET / HTTP/1.1\\r\\n\\r\\n"\n'
                '      ovh:   Обход OVH\n'
                '      avb:   Обход AVB облака\n'
                '      cfb:   Обход CloudFlare(спуффинг при этом методе не работает)\n'
                '      dgb:   Обход DDoS Guard(спуффинг при этом методе не работает)\n'
                '      bot:   Маскировка по Google bot\n'
                '      gsb:   Обход Google Project Shield\n'
                '      dyn:   Рандомный SubDomain\n'
                '      post:  Подключение к серверу и флуд post запросами\n'
                '      rhex:  Рандомный HEX\n'
                '      slow:  Slowloris метод\n'
                '      null:  Null UserAgent\n'
                '      xmlrpc: WP XMLRPC expliot (add /xmlrpc.php)\n'
                '      stress: HTTP-пакет со старшим байтом\n'
                '      cfbuam: CloudFlare Under Attack Mode Bypass\n'
                '      bypass: Обход обычного AhtiDDoS(спуффинг при этом методе не работает)\n'
                '      cookie: Random Cookie PHP\n'
                '      downloader: Медленное чтение данных\n') %
            (len(Methods.LAYER4_METHODS) + len(Methods.LAYER7_METHODS),
            ", ".join(Methods.LAYER4_METHODS), len(Methods.LAYER4_METHODS),
            ", ".join(Methods.LAYER7_METHODS), len(Methods.LAYER7_METHODS),
            ))