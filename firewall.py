from platform_config import cPlatformConfig
import time
import paramiko

sleep_time = {
    "load_sleep": 3,
    "enable_sleep": 5,
    "pwd_sleep": 3,
    "service_sleep": 5,
    "simple_wait": 2,
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

    def init_xf(self, conf:dict):
        on_ips = conf['firewall_ips'] == "true"
        settings = conf['homenet_ip']
        file_path = conf['homenet_conf_file']
        channel = self._connect()
        self.switch_ipc(channel=channel, on_ips=on_ips)
        self.configure_homenet(channel=channel, settings=settings, file_path=file_path)

    def switch_ipc(self, channel, on_ips:bool=True):
        if on_ips:
            self._start_ips(channel)
        else:
            self._stop_ips(channel)
        time.sleep(sleep_time["service_sleep"]) 
        self.log_terminal(channel)

    def configure_homenet(self, channel, settings:list, file_path:str):
        conf_str = ",".join([elem.replace("/", "\/") for elem in settings])
        print(f"Configure homenet to {conf_str} ...")
        channel.send('admin esc\n')
        time.sleep(sleep_time['pwd_sleep'])
        channel.send('Yes\n')
        time.sleep(sleep_time['pwd_sleep'])
        channel.send(self._admin_password+"\n")
        time.sleep(sleep_time['pwd_sleep'])
        self.log_terminal(channel)
        print("Inside bash xf ...")  
        channel.send(f"sed -i '/^ipvar HOME_NET/ {{ s/.*/ipvar HOME_NET {conf_str}/; }}' {file_path}\n")
        print("Try execute " + f"sed -i '/^ipvar HOME_NET/ {{ s/.*/ipvar HOME_NET {conf_str}/; }}' {file_path}\n")
        time.sleep(sleep_time['pwd_sleep'])   

    def disconnect(self):
        self._client.close()
        print("Disconnect from xf...")