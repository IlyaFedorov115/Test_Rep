import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import os

class Graph():
    def __init__(self, dict_attacker, dict_client, count_test, success_count:None) -> None:
        self._dict_attacker = dict_attacker
        self._dict_client = dict_client
        self._count_test = count_test
        self.success_count = success_count

    def graph(self):
        fig = plt.figure(tight_layout=True)
        gs = gridspec.GridSpec(4, 2)

        list_time = []
        client_succeeded = []
        pps = []
        bps = []
        pckt_size = []
        time_client = []
        reqs = []
        speed = []
        list_time_client = []

        #FROM ATTACKER
        #time from attacker_out.txt
        sec = 0
        for value in self._dict_attacker['time']:
            list_time.append(sec)
            sec+=1
        #time list from client
        sec = 1
        for value in self._dict_client['time']:
            list_time_client.append(sec)
            sec+=1
        #pps from attacker_out.txt
        for value in self._dict_attacker['pps']:
            pps.append(float(value) * 1000)
        #bps from attacker_out.txt
        for value in self._dict_attacker['bps']:
            bps.append(float(value))
        #calculate pckt_size
        i = 0
        for element in bps:
            if pps[i] == 0:
                pckt_size.append(0.0)
            else:
                pckt_size.append(bps[i]/pps[i])
            i += 1
        print("Packet size:", pckt_size)

        #FROM CLIENT
        #life of service
        for value in self._dict_client['succeeded']:
            client_succeeded.append(int(value))
        #time
        for value in self._dict_client['time']:
            time_client.append(float(value))
        #reqs
        for value in self._dict_client['reqs']:
            reqs.append(float(value))
        #speed
        for value in self._dict_client['speed']:
            speed.append(float(value))



        x_g = np.arange(1,len(list_time_client)+1,1) #For green color 
        x_r = np.arange(3,len(list_time_client)-1,1) #For red color 
        #service avialability graph
        client_succeeded_graph = fig.add_subplot(gs[0,0])
        client_succeeded_graph.plot(list_time_client, np.linspace((max(client_succeeded)*0.95), (max(client_succeeded)*0.95), len(list_time_client)), color='black')
        client_succeeded_graph.plot(list_time_client, client_succeeded)
        client_succeeded_graph.fill_between(x_g, max(client_succeeded), where=(x_g<=3) | (x_g>list_time_client[len(list_time_client)-4]),
                                        facecolor='g', alpha = 0.5)
        client_succeeded_graph.fill_between(x_r, max(client_succeeded), where=(x_r>3) | (x_r<list_time_client[len(list_time_client)-4]),
                                        facecolor='r', alpha = 0.5)      
        client_succeeded_graph.set_title('Client succeeded')
        client_succeeded_graph.set_xlabel('Number of measurement', loc='right')
        client_succeeded_graph.grid()
        #pps graph
        pps_graph = fig.add_subplot(gs[0,1])
        pps_graph.plot(list_time, pps)
        pps_graph.set_title('PPS')
        pps_graph.set_xlabel('t, sec', loc='right')
        pps_graph.grid()
        #bps graph
        bps_graph = fig.add_subplot(gs[1,1])
        bps_graph.plot(list_time, bps)
        bps_graph.set_title('BPS, kB')
        bps_graph.set_xlabel('t, sec', loc='right')
        bps_graph.grid()
        #packet size graph
        pckt_size_graph = fig.add_subplot(gs[2,1])
        pckt_size_graph.plot(list_time, pckt_size)
        pckt_size_graph.set_title('Packet size, kB')
        pckt_size_graph.set_xlabel('t, sec', loc='right')
        pckt_size_graph.grid()


        #time_h2load graph
        time_h2load_graph = fig.add_subplot(gs[1,0])
        time_h2load_graph.plot(list_time_client, time_client, 1)
        time_h2load_graph.plot(list_time_client, np.linspace(5, 5, len(list_time_client)), color='black')
        time_h2load_graph.fill_between(x_g, max(time_client), where=(x_g<=3) | (x_g>list_time_client[len(list_time_client)-4]),
                                        facecolor='g', alpha = 0.5)
        time_h2load_graph.fill_between(x_r, max(time_client), where=(x_r>3) | (x_r<list_time_client[len(list_time_client)-4]),
                                        facecolor='r', alpha = 0.5)                                
        time_h2load_graph.set_title('Time of download, sec')
        time_h2load_graph.set_xlabel('Number of measurement', loc='right')
        time_h2load_graph.grid()
        #speed client graph
        speed_graph = fig.add_subplot(gs[2,0])
        speed_graph.plot(list_time_client, speed, 1)
        speed_graph.fill_between(x_g, max(speed), where=(x_g<=3) | (x_g>list_time_client[len(list_time_client)-4]),
                                        facecolor='g', alpha = 0.5)
        speed_graph.fill_between(x_r, max(speed), where=(x_r>3) | (x_r<list_time_client[len(list_time_client)-4]),
                                        facecolor='r', alpha = 0.5)             
        speed_graph.set_title('Speed of download, MB/sec')
        speed_graph.set_xlabel('Number of measurement', loc='right')
        speed_graph.grid()
        #reqs graph
        reqs_graph = fig.add_subplot(gs[3,0])
        reqs_graph.plot(list_time_client, reqs, 1)
        reqs_graph.fill_between(x_g, max(reqs), where=(x_g<=3) | (x_g>list_time_client[len(list_time_client)-4]),
                                        facecolor='g', alpha = 0.5)
        reqs_graph.fill_between(x_r, max(reqs), where=(x_r>3) | (x_r<list_time_client[len(list_time_client)-4]),
                                        facecolor='r', alpha = 0.5)      
        reqs_graph.set_title('Request per second from client, req/s')
        reqs_graph.set_xlabel('Number of measurement', loc='right')
        reqs_graph.grid()


        if self.success_count:
            fig.suptitle(str(self._dict_attacker['info'])+"\nCount of test: "+f"{self._count_test} ({self.success_count})", color='red')
        else:
            fig.suptitle(str(self._dict_attacker['info'])+"\nCount of test: "+f"{self._count_test}", color='red')

        fig.align_labels()  # same as fig.align_xlabels(); fig.align_ylabels()

        plt.savefig(os.getcwd()+'/outs/graph.png', dpi=600)
        plt.show()

def extract_bps(s):
    bps_start = s.find('BPS: ') + 5
    bps_end = s.find(' ', bps_start)
    bps_str = s[bps_start:bps_end]
    
    bps_value = float(bps_str) if bps_str != '--' else 0
    
    bps_type_start = bps_end + 1
    bps_type_end = s.find(' ', bps_type_start)
    bps_type = s[bps_type_start:bps_type_end]
    
    return bps_value, bps_type

def extract_bps(string):
    for substring in string.split(','):
        if substring.strip().startswith('BPS:'):
            bps = substring.strip().replace('BPS:', '').strip()
            if bps == '--':
                return 0
            else:
                value, unit = bps.split(' ')
                if unit == 'B':
                    return float(value) / 1024 / 1024
                elif unit == 'kB':
                    return float(value) / 1024
                elif unit == 'MB':
                    return float(value)
                elif unit == 'GB':
                    return float(value) * 1024
    return None

def get_bps_in_mb(s):
    bps_start = s.find("BPS: ")
    if bps_start == -1:
        return None
    bps_end = s.find(" ", bps_start+len("BPS: "))
    bps_mb = 0.0
    bps_str = s[bps_start+len("BPS: "):bps_end]
    if bps_str == "--":
        bps_mb = 0.0
    else:
        bps_val = float(bps_str[:-1])
        bps_unit = bps_str[-1]
        if bps_unit == "B":
            bps_mb = bps_val / 1024 / 1024
        elif bps_unit == "k":
            bps_mb = bps_val / 1024
        elif bps_unit == "M":
            bps_mb = bps_val
        elif bps_unit == "G":
            bps_mb = bps_val * 1024
    return bps_mb


def get_bps_in_mb(s):
    bps_start = s.find("BPS: ")
    if bps_start == -1:
        return None
    bps_end = s.find(" ", bps_start+len("BPS: "))
    bps_mb = 0.0
    bps_str = s[bps_start+len("BPS: "):bps_end]
    if bps_str == "--":
        bps_mb = 0.0
    else:
        bps_val = float(bps_str[:-1])
        bps_unit = bps_str[-1]
        print(bps_unit)
        if bps_unit == "B":
            bps_mb = bps_val / 1024 / 1024
        elif bps_unit == "kB":
            bps_mb = bps_val / 1024
        elif bps_unit == "MB":
            bps_mb = bps_val
        elif bps_unit == "GB":
            bps_mb = bps_val * 1024
    return bps_mb

Смотри, на вход функции будут подаваться строка (ниже три примера):
[04:39:49 - DEBUG] Target: 192.168.56.77, Port: 443, Method: GET, PPS: 780.30k, BPS: -- B / 6%
[04:39:49 - DEBUG] Target: 192.168.56.77, Port: 443, Method: GET, PPS: 780.30k, BPS: 518.03 MB / 6%
[04:39:49 - DEBUG] Target: 192.168.56.77, Port: 443, Method: GET, PPS: 780.30k, BPS: 1.30 GB / 6%
Напиши функцию, которая вернет значение BPS в MB. На примерах строк видно, что если "--", то это 0. Также видно, что BPS может быть представлен в разных форматах. Но вернуть надо в MB. Размер которые могут встречаться: "B", "kB", "MB", "GB".

    
def get_bps_in_mb(log_str):
    bps_str = log_str.split(", ")[-1].split(": ")[-1]
    if bps_str == "-- B / 6%":
        return 0
    bps_val, bps_unit = bps_str.split()
    bps_val = float(bps_val)
    if bps_unit == "kB":
        bps_val /= 1024
    elif bps_unit == "GB":
        bps_val *= 1024
    elif bps_unit != "MB":
        raise ValueError("Unexpected BPS unit: {}".format(bps_unit))
    return bps_val

import re
def extract_bps(string):
    # Используем регулярное выражение для извлечения значения BPS и его единицы измерения
    pattern = r'BPS: (--|\d+\.\d+) ([KMG]?B) / (\d+)%'
    UNITS = {
    'B': 1/1024/1024,
    'kB': 1/1024,
    'MB': 1,
    'GB': 1024,
    }
    match = re.search(pattern, string)
    if match:
        bps_str = match.group(1)
        if bps_str == "--":
            bps_value = 0.0
        else:
            bps_value = float(bps_str)
        bps_unit = match.group(2)
        mb_value = bps_value * UNITS[bps_unit] #/ UNITS['MB']
        return mb_value
    else:
        return None

def get_pps(string):
    # Ищем первое вхождение "PPS:" в строке
    start_index = string.find("PPS:") + 5
    # Ищем первый символ, отличный от цифр и точки, после значения PPS
    end_index = start_index
    while end_index < len(string) and string[end_index].isdigit() or string[end_index] == ".":
        end_index += 1
    # Извлекаем значение PPS из строки
    print(pps_value)
    pps_value = string[start_index:end_index]
    # Конвертируем PPS в число
    print(pps_value)
    if pps_value[-1] == 'k':
        pps_value = float(pps_value[:-1]) * 1000
    elif pps_value[-1] == 'm':
        pps_value = float(pps_value[:-1]) * 1000000
    else:
        pps_value = float(pps_value)
    return pps_value


def parse_pps(string):
    pps_pattern = r"PPS: (\d*\.?\d+)([kmg]?)"
    pps_value, pps_unit = re.search(pps_pattern, string).groups()
    UNITS = {"": 1, "k": 1000, "M": 1000000, "G": 1000000000}
    return float(pps_value) * UNITS[pps_unit]
