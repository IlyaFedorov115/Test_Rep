import argparse
import time
from graph import Graph
from threading import Thread, Event
from console import ToolsConsole
from platform_config import cPlatformConfig
from devlib import  LinuxTarget
from attacker import cAttacker
#from nginx import cNginx
from client import cClient
from web import cWeb
from firewall import cFirewall
from video_analysis import VideoProcessor
import subprocess
import os

def clean_directory(directory_path, extensions):
    if not os.path.exists(directory_path):
        return
    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        if os.path.isfile(filepath) and filename.split('.')[-1] in extensions:
            os.remove(filepath)

def clean_work_space(pconfig):
    extensions_to_delete = ['txt', 'mkv', 'avi', 'csv', 'png']
    directory_path = pconfig.getVideoProcessLclWorkDir()+pconfig.getVectorOfAttack()+"/"
    clean_directory(directory_path, extensions_to_delete)
    directory_path = './outs/' + pconfig.getVectorOfAttack()+"/"
    clean_directory(directory_path, extensions_to_delete)  

def make_test(pconfig:cPlatformConfig, graph_show=True):
    print(f"==========={pconfig.getVectorOfAttack().upper()}=============")
    print('Create machines...')
    use_clone = pconfig.getIsUseClone()
    lt_attacker = LinuxTarget(pconfig.getSSHNetworkAttacker().copy())
    lt_client = LinuxTarget(pconfig.getSSHNetworkClient().copy())
    lt_web = LinuxTarget(pconfig.getSSHNetworkWeb().copy())
    lt_web_attack = LinuxTarget(pconfig.getSSHNetworkWebAttack().copy())
    if use_clone: lt_firewall = LinuxTarget(pconfig.getNetworkFirewall())
    print('Start tests...')
    for count_exp in range(1,int(pconfig.getCountOfTests())+1):
        print('Sleep before load machines...')
        time.sleep(pconfig.getWarmUpTime())
        print("\n===============\nTEST №", count_exp)
        #init machines
        attacker = cAttacker(pconfig, lt_attacker, count_exp)
        client = cClient(pconfig, lt_client, count_exp)
        web = cWeb(pconfig, lt_web)
        if use_clone: web_attack = cWeb(pconfig, lt_web_attack)
        #firewall = cFirewall(lt_firewall)

        #init, push and chmod scripts
        attacker.init_script(ttl=pconfig.getSSHTimeout())
        client.init_script(ttl=pconfig.getSSHTimeout())
        web.init_script(use_vlc_receive=True, ttl=pconfig.getSSHTimeout())
        if use_clone: web_attack.init_script(ttl=pconfig.getSSHTimeout())

        if count_exp == 1: web.clean_videos_dir()
        #firewall.connect()

        #routing settings on web machine after reboot
        web.start_script()
        if use_clone: web_attack.start_script()
        
        # first time load orig video
        if count_exp == 1: client.load_video()

        #connecting to machines and start scripts
        test_before_attack = Event()
        attack_started = Event()
        attack_ended = Event()
        attacker_thread = Thread(target=attacker.start_script, args=(attack_ended, attack_started, test_before_attack,))
        client_thread = Thread(target=client.start_script, args=(attack_ended, attack_started, test_before_attack,web,))
        attacker_thread.start()
        client_thread.start()
        attacker_thread.join()
        client_thread.join()

        # load only one pack of videos
        if count_exp == 1:
            print("Downloading videos from web...")
            web.load_videos()
            web.send_video()

        if count_exp == int(pconfig.getCountOfTests()):
            web.load_remote_stat()

        web_thread = Thread(target=web.reboot)
        #firewall_thread = Thread(target=firewall.reboot)
        web_thread.start()
        #firewall_thread.start()
        web_thread.join()

        if use_clone:
            print("Reboot attacked web...")
            web_thread = Thread(target=web_attack.reboot)
            web_thread.start()
            web_thread.join()
        #firewall_thread.join()
        #lt_attacker.disconnect()

    #graph drawing
    client_avg, success_count = client.parse_out()
    print('Start to draw...')
    graph = Graph(attacker.parse_out(), client_avg, pconfig.getCountOfTests(), success_count)
    graph.graph(pconfig, graph_show)

    #video graphs
    video_graph = VideoProcessor(pconfig)
    video_graph.process_analysis_videos(graph_show=graph_show)
    #video_graph.made_demonstation()  


def main():
    #parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True, type=str, help = "Full path to platform_config.json")
    args = parser.parse_args()
    
    #init config and targets
    pconfig = cPlatformConfig(args.config)
    if pconfig.checkJson()==-1:
        raise SystemExit

    #ips on xf
    firewall = cFirewall(pconfig.getSSHNetworkFirewall(), 
                         admin_password=pconfig.getNetworkFirewallAdmin())
    firewall.switch_ipc(on_ips=pconfig.getUseFirewallIPS())
    firewall.disconnect()

  
    if pconfig.getVectorIsAll():
        attacks = pconfig.getSupportedVectors()
        for attack in attacks:
            pconfig.setVectorAttack(attack)
            clean_work_space(pconfig)        
            make_test(pconfig, graph_show=False)
    else:
        clean_work_space(pconfig)        
        make_test(pconfig, graph_show=True)

def main1():
    #parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True, type=str, help = "Full path to platform_config.json")
    args = parser.parse_args()
    
    #init config and targets
    pconfig = cPlatformConfig(args.config)
    if pconfig.checkJson()==-1:
        raise SystemExit

    directory_path = pconfig.getVideoProcessLclWorkDir()+pconfig.getVectorOfAttack()+"/"
    extensions_to_delete = ['txt', 'mkv', 'avi', 'csv', 'png']
    clean_directory(directory_path, extensions_to_delete)
    directory_path = './outs/' + pconfig.getVectorOfAttack()+"/"
    clean_directory(directory_path, extensions_to_delete)

    print('Create machines...')
    lt_attacker = LinuxTarget(pconfig.getSSHNetworkAttacker())
    lt_client = LinuxTarget(pconfig.getSSHNetworkClient())
    lt_web = LinuxTarget(pconfig.getSSHNetworkWeb())
    #lt_firewall = LinuxTarget(pconfig.getNetworkFirewall())
    print('Start tests...')

    for count_exp in range(1,int(pconfig.getCountOfTests())+1):
        print('Sleep before load machines...')
        time.sleep(pconfig.getWarmUpTime())
        print("\n===============\nTEST №", count_exp)
        #init machines
        attacker = cAttacker(pconfig, lt_attacker, count_exp)
        client = cClient(pconfig, lt_client, count_exp)
        web = cWeb(pconfig, lt_web)
        #firewall = cFirewall(lt_firewall)

        #init, push and chmod scripts
        attacker.init_script()
        client.init_script()
        web.init_script(use_vlc_receive=True)

        if count_exp == 1: web.clean_videos_dir()
        #firewall.connect()

        #routing settings on web machine after reboot
        web.start_script()
        
        # first time load orig video
        if count_exp == 1: client.load_video()

        #connecting to machines and start scripts
        test_before_attack = Event()
        attack_started = Event()
        attack_ended = Event()
        attacker_thread = Thread(target=attacker.start_script, args=(attack_ended, attack_started, test_before_attack,))
        client_thread = Thread(target=client.start_script, args=(attack_ended, attack_started, test_before_attack,web,))
        attacker_thread.start()
        client_thread.start()
        attacker_thread.join()
        client_thread.join()

        # load only one pack of videos
        if count_exp == 1:
            print("Downloading videos from web...")
            web.load_videos()
            web.send_video()

        if count_exp == int(pconfig.getCountOfTests()):
            web.load_remote_stat()

        web_thread = Thread(target=web.reboot)
        #firewall_thread = Thread(target=firewall.reboot)
        web_thread.start()
        #firewall_thread.start()
        web_thread.join()
        #firewall_thread.join()

    #graph drawing
    client_avg, success_count = client.parse_out()
    print('Start to draw...')
    graph = Graph(attacker.parse_out(), client_avg, pconfig.getCountOfTests(), success_count)
    graph.graph(pconfig)

    #video graphs
    video_graph = VideoProcessor(pconfig)
    video_graph.process_analysis_videos()
    video_graph.made_demonstation()


if __name__ == '__main__':
    ToolsConsole.usage()
    main()
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True,
                        type=str, help="Full path to platform_config.json")
    args = parser.parse_args()
    pconfig = cPlatformConfig(args.config)
    attacker = cAttacker(pconfig, None, 1)
    client = cClient(pconfig, None, 1)
    web = cWeb(pconfig, None)
    client_avg, success_count = client.parse_out()
    print('Start to draw...')
    graph = Graph(attacker.parse_out(), client_avg,
                  pconfig.getCountOfTests(), success_count)
    graph.graph(pconfig)

    # video graphs
    video_graph = VideoProcessor(pconfig)
    video_graph.process_analysis_videos()
    video_graph.made_demonstation()
    '''
    #video_graph.made_demonstation()
    
	"use_clone": "false",
    def getIsUseClone(self):
        return self._config["use_clone"] == "true"
