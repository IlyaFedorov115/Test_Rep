import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import os
from platform_config import cPlatformConfig


class Graph():
    def __init__(self, dict_attacker, dict_client, count_test, success_count:None) -> None:
        self._dict_attacker = dict_attacker
        self._dict_client = dict_client
        self._count_test = count_test
        self.success_count = success_count

    def graph(self, pconfig:cPlatformConfig, graph_show:True):
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
            #pps.append(float(value) * 1000)
            pps.append(float(value))
        #bps from attacker_out.txt
        for value in self._dict_attacker['bps']:
            bps.append(float(value))
        #calculate pckt_size
        i = 0
        for element in bps:
            if pps[i] == 0:
                pckt_size.append(0.0)
            else:
                pckt_size.append(bps[i]*1024/pps[i])
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
        bps_graph.set_title('BPS, MB')
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
        time_h2load_graph.plot(list_time_client, np.linspace(int(pconfig.getTimeoutClient()), int(pconfig.getTimeoutClient()), len(list_time_client)), color='black')
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

        plt.savefig(os.getcwd()+'/outs/'+pconfig.getVectorOfAttack()+'/graph.png', dpi=600)
        
        if graph_show:
            plt.show()