import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import os
from platform_config import cPlatformConfig
import pandas as pd
from files_path import ClientPaths
import client

class Graph():
    def __init__(self,pconfig:cPlatformConfig) -> None:
        self._cfg = pconfig

    def plot_method_graph(self, dict_attacker, graph_show:True):
        pconfig = self._cfg
        self._dict_attacker = dict_attacker
        pconfig = self._cfg
        list_time, client_succeeded = [], []
        pps, bps = [], []
        pckt_size, time_client = [], []
        reqs, speed, list_time_client = [], [], []
        #FROM ATTACKER
        #time from attacker_out.txt
        sec = 0
        for value in self._dict_attacker['time']:
            list_time.append(sec)
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

        fig = plt.figure(figsize=(12,8), tight_layout=False)
        gs = gridspec.GridSpec(4, 2)
        #gs.set_height_ratios()
        # pps, bps packet size graphs
        titles = ['PPS', 'BPS, MB', 'Packet size, kB']
        curr_data = [pps, bps, pckt_size]
        for index, (title, data) in enumerate(zip(titles, curr_data)):
            gr = fig.add_subplot(gs[index,1])
            gr.plot(list_time, data)
            gr.set_title(title)
            gr.set_xlabel('t, sec', loc='right')
            gr.grid()

        # plot h2load
        self._plot_method_h2load(gs=gs, fig=fig)

        fig.align_labels()  # same as fig.align_xlabels(); fig.align_ylabels()
        fig.suptitle(self.make_title_method(pconfig=pconfig), color="black")
        plt.savefig(os.getcwd()+'/outs/'+pconfig.getVectorOfAttack()+'/graph.png', dpi=1000)       
        if graph_show:
            plt.show()

    def make_title_method(self, pconfig:cPlatformConfig)->str:
        return f"Attack with '{pconfig.getVectorOfAttack()}' method. " + \
               f"Tests: {pconfig.getCountOfTests()}."


    def _plot_method_h2load(self, gs:gridspec.GridSpec, fig:plt.figure):
        '''
        plot graph for one method
        '''
        pconfig = self._cfg
        count_of_tests = int(pconfig.getCountOfTests())
        success_count = int(pconfig.getCountOfClient())
        time_launch = int(pconfig.getLaunchTime())
        
        def _get_data(prefix:str):
            nonlocal count_of_tests
            sum_df = client.cClient._parse_out_all_csv(pconfig, prefix)
            mean_df = client.cClient._parse_out_mean_csv(sum_df, int(self._cfg.getCountOfTests()))
            return mean_df.rename(columns=lambda x: x.replace(' ', ''))

        def _plot(data:list, xlabel, ylabel, len_measured, label:list, gf_ind=[0,0]):
            nonlocal fig, gs, mean_df, time_launch
            curr = fig.add_subplot(gs[gf_ind[0],gf_ind[1]])
            for data_, label_ in zip(data, label):
                curr.plot(data_, label=label_)
            #curr.set_xticks(range(len(mean_df)), np.arange(time_launch, (len(mean_df)+1) * time_launch, time_launch))
            curr.set_xticks(range(len_measured), np.arange(time_launch, (len_measured+1) * time_launch, time_launch))
            curr.set_xlabel(xlabel)
            curr.set_ylabel(ylabel)
            curr.legend()
            curr.grid(True)
            return curr
        
        # plot  during attack
        mean_df = _get_data(pconfig.getLoadLogPrefix()[1])
        _plot([mean_df['count'] * 100 / success_count], 'Time launch (sec)', 'Success count %', 
              len(mean_df) , ["during"] ,[0,0]).plot(np.linspace(95, 95, len(mean_df)), color='black', linestyle='--')
        
        sec_coef = 1e6
        _plot([mean_df['avg']/sec_coef], 'Time launch (sec)', 'Avg req time (s)', len(mean_df) , ["during"] , [1,0])
        # plot before and after attack
        mean_df_before = _get_data(pconfig.getLoadLogPrefix()[0])
        mean_df_after = _get_data(pconfig.getLoadLogPrefix()[2])
        _plot([mean_df_before['count']*100/success_count, mean_df_after['count']*100/success_count], 
                'Time launch (sec)', 'Success count %', len(mean_df_before) , 
                ['before', 'after'], [2,0]).plot(np.linspace(95, 95, len(mean_df_before)), color='black', linestyle='--')
        _plot([mean_df_before['avg']/sec_coef, mean_df_after['avg']/sec_coef], 'Time launch (sec)', 'Avg req time (s)', 
              len(mean_df_before), ['before', 'after'] ,[3,0])
        
    @staticmethod
    def plot_inter_graph(pconfig:cPlatformConfig):
        if not pconfig.getVectorIsAll(): print('[WARNING] Config file don`t set use  all methods.')
        success_count = int(pconfig.getCountOfClient())       
        list_methods = pconfig.getSupportedVectors()
        prefix = pconfig.getLoadLogPrefix()[1]
        attack_results = {}
        mean_values_dict = {}
        mean_values = []


        fig = plt.figure(figsize=(10,6), tight_layout=False)
        gs = gridspec.GridSpec(1, 2)
        #gs.set_height_ratios()
        # pps, bps packet size graphs
        titles = ['PPS', 'BPS, MB', 'Packet size, kB']
        curr_data = [pps, bps, pckt_size]
        for index, (title, data) in enumerate(zip(titles, curr_data)):
            gr = fig.add_subplot(gs[index,1])
            gr.plot(list_time, data)
            gr.set_title(title)
            gr.set_xlabel('t, sec', loc='right')
            gr.grid()


        for method in list_methods:
            pconfig.setVectorAttack(method)
            sum_df = client.cClient._parse_out_all_csv(pconfig=pconfig, prefix=prefix)
            mean_df = client.cClient._parse_out_mean_csv(sum_df, int(pconfig.getCountOfTests()))
            attack_results[method] = mean_df
        for key in attack_results.keys():
            mean_values_dict[key] = attack_results[key]['count'].mean()
            mean_values.append(attack_results[key]['count'].mean())
        mean_values = np.array(mean_values)
        mean_values = mean_values * 100 / success_count
        plt.vlines(x=attack_results.keys(), ymin=0, ymax=mean_values, color='firebrick')
        plt.scatter(x=attack_results.keys(), y=mean_values, color='firebrick')
        plt.ylabel('Success %')
        plt.xlabel('Attack type')
        for key in mean_values_dict.keys():
            plt.text(key, mean_values_dict[key]+np.mean(mean_values)*0.03, s=round(mean_values_dict[key], 2), horizontalalignment= 'center', verticalalignment='bottom', fontsize=7)
        plt.show()