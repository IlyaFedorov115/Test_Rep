import json
from importlib.metadata import files
from itertools import islice


class cPlatformConfig:
    def __init__(self,path_to_config):
        self._config=json.loads(open(path_to_config,'r').read())

    #Check config
    def checkJson(self):
        if int(self.getTimeOfAttack()) < int(self.getTimeoutClient()):
            print("ERROR params in json!\ntime_of_attack must be greater or equals than timeout_client\n")
            return -1

    #Params
    def getCountOfTests(self)->{}:
        return self._config["count_of_tests"]

    def getTimeOfAttack(self)->{}:
        return self._config["time_of_attack"]

    def getVectorOfAttack(self)->{}:
        return self._config["vector_of_attack"]

    def getPortOfAttack(self)->{}:
        return self._config["port_of_attack"]

    def getSpoofing(self)->{}:
        return self._config["spoofing"]
    
    def getRpc(self)->{}:
        return self._config["rpc"]

    # h2load params
    def _getUtilParam(self, name):
        return self._config["load_testing"][name]

    def getCountOfClient(self):
        return self._getUtilParam("count_of_client")

    def getThreadsClient(self):
        return self._getUtilParam("threads_client")

    def getTimeoutClient(self):
        return self._getUtilParam("timeout_client")

    def getWebHtml(self)->{}:
        return self._getUtilParam("web_html")

    def getaunchNumNormal(self):
        return self._getUtilParam("num_launch_normal")

    def getLaunchTime(self):
        return self._getUtilParam("time_launch")

    def getNumLaunchNormal(self):
        return self._getUtilParam("num_launch_normal")  
    
    def getLoadLogPrefix(self):
        return self._getUtilParam("log_file_prefix")  

    def getLoadUtilPath(self):
        return self._getUtilParam("util_path")     

    def getLoadLogCsv(self):
        return self._getUtilParam("csv_out") 
    
    def getLoadLogDir(self):
        return self._getUtilParam("log_dir") 

    def getLoadSaveInterLogs(self):
        return self._getUtilParam("save_inter_logs").lower() == "yes"

    def getClientWorkDir(self)->str:
        return self._config["client_work_dir"]

    def getUseVideo(self):
        return self._config["use_video"].lower() == "yes"
    
    def getTimeOfVideo(self):
        return int(self._config["time_of_video"])

    def getWorkDir(self)->str:
        wd=self._config["work_dir"]
        if(len(wd)<8):
          raise
        return wd

    def getMhddosDir(self)->{}:
        wd=self._config["mhddos_dir"]
        if(len(wd)<8):
          raise
        return wd
    
    def getIsUseClone(self):
        return self._config["use_clone"] == "true"
    
    def getNetworkBindwith(self):
        return self._config["network_bandwith"]
    
    def getWarmUpTime(self):
        return int(self._config["warm_up_time"])

    def getVectorIsAll(self):
        return self._config["vector_of_attack"].lower() == "all"
        
    def getSupportedVectors(self):
        return self._config["supported_vectors"]
        
    def setVectorAttack(self, vector):
        self._config["vector_of_attack"] = vector

    def getSSHTimeout(self):
        return int(self._config["ssh_timeout"])

    def getNetworkFirewallAdmin(self):
        return self._config["network_config"]["firewall"]["admin_password"]

    def getSSHNetwork(self, name)->{}:
        return self._config["network_config"][name]["ssh_settings"]
    def getNetworkHost(self, name):
        return self._config["network_config"][name]["work_host"]
    

    def getFirewallSettings(self):
        return self._config["xf_config"]
    def _getFirewallSetting(self, name):
        return self._config["xf_config"][name]
    def getUseFirewallIPS(self):
        return self._getFirewallSetting("firewall_ips") == "true"
    def getFirewallHomenet(self):
        return self._getFirewallSetting("homenet_ips")
        
    #Attacker
    def getNetworkAttacker(self)->{}:
        return self._config["network_config"]["attacker"]
    def getNetworkAttackerHost(self):
        return self.getNetworkHost("attacker")
    def getNetworkAttackerInterface(self)->{}:
        return self._config["attacker_iface"]
    def getSSHNetworkAttacker(self)->{}:
        return self.getSSHNetwork("attacker")
    #Web
    def getNetworkWeb(self)->{}:
        return self._config["network_config"]["web"]
    def getNetworkWebHost(self)->{}:
        return self.getNetworkHost("web")
    def getNetworkWebInterface(self)->{}:
        return self._config["web_iface"]
    def getSSHNetworkWeb(self)->{}:
        return self.getSSHNetwork("web")
    #Web attack
    def getNetworkWebAttack(self)->{}:
        return self._config["network_config"]["web_attack"]
    def getNetworkWebAttackHost(self)->{}:
        return self.getNetworkHost("web_attack")
    def getSSHNetworkWebAttack(self)->{}:
        return self.getSSHNetwork("web_attack")
    #Client
    def getNetworkClient(self)->{}:
        return self._config["network_config"]["client"]
    def getNetworkClientHost(self):
        return self.getNetworkHost("client")
    def getNetworkClientInterface(self)->{}:
        return self._config["client_iface"]
    def getSSHNetworkClient(self)->{}:
        return self.getSSHNetwork("client")
    #Firewall
    def getNetworkFirewall(self)->{}:
        return self._config["network_config"]["firewall"]
    def getNetworkFirewallHost(self)->{}:
        return self.getNetworkHost("firewall")
    def getNetworkFirewallInterface(self)->{}:
        return self._config["fw_iface"]
    def getSSHNetworkFirewall(self)->{}:
        return self.getSSHNetwork("firewall")
    # Video
    def getVideoProcess(self)->{}:
        return self._config["video_processing_config"]
    def getVideoProcessOrigVideo(self):
        return self._config["video_processing_config"]["orig_video"]
    def getVideoProcessFormat(self):
        return self._config["video_processing_config"]["format_2_save"]
    def getVideoProcessOutCsv(self):
        return self._config["video_processing_config"]["output_csv_file"]
    def getVideoProcessLclWorkDir(self):
        return self._config["video_processing_config"]["local_work_dir"]
    def getVideoProcessRmtWorkDir(self):
        return self._config["video_processing_config"]["remote_work_dir"]
    def getVideoProcessNames(self):
        return self._config["video_processing_config"]["video_names"]
    def getVideoPortSndRcv(self):
        return self._config["video_processing_config"]["port_snd_rcv"]