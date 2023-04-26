from console import ToolsConsole
from platform_config import cPlatformConfig
import devlib
from devlib import LinuxTarget, Target
from attacker import cAttacker
#from nginx import cNginx
from client import cClient
from web import cWeb
from firewall import cFirewall
from video_analysis import VideoProcessor
import subprocess
import os
import argparse
import time
import paramiko


def log_terminal(channel):
        # ожидаем, пока команда "enable" завершится и выведет результат
    while not channel.recv_ready():
        pass

    # получаем и выводим на экран результат выполнения команды "enable"
    output = channel.recv(1024).decode("utf-8")
    print(output)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True, type=str, help = "Full path to platform_config.json")
    args = parser.parse_args()
    
    #init config and targets
    pconfig = cPlatformConfig(args.config)
    if pconfig.checkJson()==-1:
        raise SystemExit
    
    ssh_settings = pconfig.getSSHNetworkFirewall()
    
    client = paramiko.SSHClient()

    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ssh_settings['host'], username=ssh_settings['username'], 
                   password=ssh_settings['password'])

    time.sleep(1)
    channel = client.invoke_shell()

    log_terminal(channel)

    channel.send("enable\n")
    time.sleep(5)
    log_terminal(channel)
    channel.send(f"{pconfig.getNetworkFirewallAdmin()}\n")

   
    time.sleep(2)
    print("Start")
    channel.send("service ips start\n")
    time.sleep(5)
    log_terminal(channel)

    channel.send("service ips show status\n")
    time.sleep(2)
    log_terminal(channel)
    client.close()

    #lt_firewall = Target()(pconfig.getSSHNetworkFirewall().copy(), connect=True)
    #admin_password = pconfig.getNetworkFirewallAdmin()
    #lt_firewall.connect(timeout=500,check_boot_completed=True)
    '''
    try:
        lt_firewall.connect(timeout=500, check_boot_completed=False)
    except devlib.exception.TargetStableError:
        pass
    '''
    #t_firewall.execute("enable")
    #time.sleep(2)
    #lt_firewall.execute(admin_password)
    #time.sleep(2)
    #lt_firewall.execute("service ips start")

main()