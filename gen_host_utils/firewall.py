from platform_config import cPlatformConfig
import time
import paramiko

sleep_time = {
    "load_sleep": 3,
    "enable_sleep": 5,
    "pwd_sleep": 3,
    "service_sleep": 5
}

class cFirewall:
    def __init__(self, config:dict, admin_password:str):
        self._client = paramiko.SSHClient()
        self._hostname = config['host']
        self._username = config['username']
        self._password = config['password']
        self._admin_password = admin_password
        if "port" in config:
            self._port = int(config['port'])
        else:
            self._port = 22
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def log_terminal(self, channel):
        while not channel.recv_ready():
            pass
        output = channel.recv(1024).decode("utf-8")
        print(output)
    
    def _connect(self):
        self._client.connect(hostname=self._hostname,
                             port=self._port,
                             username=self._username,
                             password=self._password)
        print('Connect to xf...')
        time.sleep(sleep_time["load_sleep"])
        
        channel = self._client.invoke_shell()

        channel.send("enable\n")
        print('Trying enable xf...')
        time.sleep(sleep_time["enable_sleep"])
        channel.send(self._admin_password+"\n")
        time.sleep(sleep_time["pwd_sleep"])
        print('End enable xf...')
        return channel


    def _stop_ips(self, channel):
        print('Stop ips on xf...')
        channel.send("service ips stop\n")

    def _start_ips(self, channel):
        print('Start ips on xf...')
        channel.send("service ips start\n")

    def switch_ipc(self, on_ips:bool=True):
        channel = self._connect()
        if on_ips:
            self._start_ips(channel)
        else:
            self._stop_ips(channel)
        time.sleep(sleep_time["service_sleep"]) 


    def disconnect(self):
        self._client.close()
        print("Disconnect from xf...")
