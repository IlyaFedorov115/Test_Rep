import time
from platform_config import cPlatformConfig
from devlib import LinuxTarget
from console import Methods
import re

class cAttacker:
    def __init__(self,config:cPlatformConfig,target:LinuxTarget, count_exp, use_clone:bool):
        self._cfg = config
        self._trg = target
        self._count_exp = count_exp
        self._use_clone = use_clone

    def init_script(self, ttl=200)->str:
        local_init_path=self._cfg.getWorkDir()+"scripts/attacker.sh"
        remote_script_path = self._cfg.getMhddosDir()+ "attacker.sh"

        #create script
        answer='#!/bin/bash\n'
        answer+="\nip r del "
        answer+=('.'.join(self._cfg.getNetworkAttackerHost().split('.')[:-1])) + ".0/24\n"
        answer+="python3 "+self._cfg.getMhddosDir()+"start.py " 
        answer+=self._cfg.getVectorOfAttack()+" "+self._cfg.getSpoofing()+" "
        if (self._cfg.getPortOfAttack() == "80"):
            answer+="http://"
        elif (self._cfg.getPortOfAttack() == "443"):
            answer+="https://"
        attacked_web = self._cfg.getNetworkWebAttackHost() if self._use_clone else self._cfg.getNetworkWebHost()
        answer+=attacked_web+":"+self._cfg.getPortOfAttack()+" "
        if (self._cfg.getVectorOfAttack().lower() in Methods.LAYER7_METHODS):
            answer+=self._cfg.getRpc()+" "
        answer+=self._cfg.getTimeOfAttack() + " " + self._cfg.getNetworkBindwith() + " "  + self._cfg.getSpoofing() + " \n" #" true\n"
        with open(local_init_path,'w') as tmp_file:
            tmp_file.write(answer)
        print("Attacker: " + answer)
        #push and chmod script
        print(local_init_path)
        print(remote_script_path)
        print("Connecting to attacker machine...")
        self._trg.connect(timeout=ttl,check_boot_completed=True)
        self._trg.push(local_init_path, remote_script_path)
        self._trg.execute("chmod 777 " + remote_script_path)

    def start_script(self, attack_ended, attack_started, test_before_attack):
        while not test_before_attack.is_set():
            continue

        cmd="nohup bash "+self._cfg.getMhddosDir()+'attacker.sh'+" > "+self._cfg.getMhddosDir()+"attacker_log_"+str(self._count_exp)+".txt &"
        print(cmd)
        print("Attack is started")
        attack_started.set()
        self._trg.execute(cmd)
        print("Attack is ended")
        attack_ended.set()
        print("Downloading out from attacker...")
        self._trg.pull(self._cfg.getMhddosDir()+"attacker_log_"+str(self._count_exp)+".txt", str(self._cfg.getWorkDir())+"outs/"+self._cfg.getVectorOfAttack()+"/out_attacker_"+str(self._count_exp)+".txt")
        reboot(self)
        #print("Attacker: sleeping 60 sec. Waiting rebooting of machine...")
        #time.sleep(60)
        
    def parse_out(self):
        avg_dict = dict()
        avg_dict.update({'time': []})
        avg_dict.update({'pps': []})
        avg_dict.update({'bps': []})
        avg_dict.update({'info': []})
        dict_exp = []
        #parse all outputs
        for count_exp in range(0,int(self._cfg.getCountOfTests())):
            dict_exp.append({})
            with open(self._cfg.getWorkDir()+"outs/"+self._cfg.getVectorOfAttack()+"/out_attacker_"+str(count_exp+1)+".txt",'r') as tmpFile:
                content = list(filter(None, tmpFile.read().split('\n')))
                dict_exp[count_exp].update({'time': []})
                dict_exp[count_exp].update({'pps': []})
                dict_exp[count_exp].update({'bps': []})
                dict_exp[count_exp].update({'info': []})
                dict_exp[count_exp]['info'].append(content[0][18:])
                content.pop(0)
                for el in content:
                    dict_exp[count_exp]['time'].append(el[1:9])
                    dict_exp[count_exp]['pps'].append(get_pps(el))
                    dict_exp[count_exp]['bps'].append(get_bps(el))
                print("Out №%d from attacker: \n" % (count_exp+1), dict_exp[count_exp], "\n")
        #average to avg dict
        for number_measurement in range(0,int(self._cfg.getTimeOfAttack())):
            for key in ['pps','bps']:
                sum = 0
                for count_exp in range(0,int(self._cfg.getCountOfTests())):
                    sum+=float(dict_exp[count_exp][key][number_measurement])
                avg_dict[key].append(sum/int(self._cfg.getCountOfTests()))
        #copy time
        for el in range(0,int(self._cfg.getTimeOfAttack())):
            avg_dict['time'].append(dict_exp[0]['time'][el])
        avg_dict['info'].append(dict_exp[0]['info'])
        print(print("Average from attacker: \n", avg_dict))
        return avg_dict
            
        
def get_pps(string):
    pps_pattern = r"PPS: (\d*\.?\d+)([kmg]?)"
    pps_value, pps_unit = re.search(pps_pattern, string).groups()
    UNITS = {"": 1, "k": 1000, "m": 1000000, "g": 1000000000}
    return float(pps_value) * UNITS[pps_unit]

def get_bps(string):
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
        return 0.0

def reboot(self):
        print("Attacker machine:rebooting...")
        self._trg.reboot(connect=False)