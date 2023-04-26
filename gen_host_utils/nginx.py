import time

from platform_config import cPlatformConfig
from devlib import LinuxTarget

class cNginx:
    def __init__(self, config: cPlatformConfig, target: LinuxTarget):
        self._cfg = config
        self._trg = target

    def init_script(self)->str:
        local_init=self._cfg.getWorkDir()+"/init.sh"
        remote_script_path = '/root/init.sh'

        #create script
        answer='#!/bin/bash\n'
        answer+="ip route add 10.10.3.0/24 via 10.10.4.1 \n"
        with open(local_init,'w') as tmp_file:
            tmp_file.write(answer)

        #push and execute script
        self._trg.push(local_init, remote_script_path)
        self._trg.execute("chmod 777 " + remote_script_path)

    def init(self,ttl=200):
        print("Connecting to nginx machine...")
        self._trg.connect(timeout=ttl,check_boot_completed=False)
        time.sleep(15)
        print("nginx reboot DONE")
        cmd="nohup bash " + '/root/init.sh' + " > init_log.txt &"
        print(cmd)
        print(self._trg.execute(cmd))

    def reboot(self):
        print("nginx: rebooting")
        self._trg.reboot(connect=False)


