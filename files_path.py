import time
from platform_config import cPlatformConfig
from devlib import LinuxTarget
from web import cWeb
import pprint
import re
import os


'''
Client functions
'''
class ClientPaths:
    @staticmethod
    def get_remote_log_dir(pconfig:cPlatformConfig):
        return os.path.join(pconfig.getClientWorkDir(),
                            pconfig.getLoadLogDir())

    @staticmethod
    def get_local_log_dir(pconfig:cPlatformConfig):
        return os.path.join(pconfig.getWorkDir(),
                                     "outs/",
                                     pconfig.getVectorOfAttack(),
                                     pconfig.getLoadLogDir())

    @staticmethod
    def get_remote_log_main(pconfig:cPlatformConfig, prefix:str, num_test:int)->str:
        '''
        Main log - log of bash script work (with errors)
        '''
        return os.path.join(ClientPaths.get_remote_log_dir(pconfig), f"{prefix}{str(num_test)}.txt")
    
    @staticmethod
    def get_local_log_main(pconfig:cPlatformConfig, prefix:str, num_test:int)->str:
        return os.path.join(ClientPaths.get_local_log_dir(pconfig), f"{prefix}{str(num_test)}.txt")
    
    @staticmethod
    def get_remote_log_csv(pconfig:cPlatformConfig, prefix:str, num_test:int):
        '''
        Csv log - log with need stats from h2load, interrupt by time 
        '''
        return os.path.join(ClientPaths.get_remote_log_dir(pconfig), 
                            f"{prefix}{str(num_test)}{pconfig.getLoadLogCsv()}.csv")

    @staticmethod
    def get_local_log_csv(pconfig:cPlatformConfig, prefix:str, num_test:int)->str:
        return os.path.join(ClientPaths.get_local_log_dir(pconfig), 
                            f"{prefix}{str(num_test)}{pconfig.getLoadLogCsv()}.csv")

    @staticmethod
    def get_local_script(pconfig:cPlatformConfig, name="client"):
        return os.path.join(pconfig.getWorkDir(), "scripts", f"{name}.sh")

    @staticmethod
    def get_remote_script(pconfig:cPlatformConfig, name="client"):
        return os.path.join(pconfig.getClientWorkDir(), f"{name}.sh")

    @staticmethod
    def get_remote_orig_video(pconfig:cPlatformConfig):
        return os.path.join(pconfig.getClientWorkDir(), pconfig.getVideoProcessOrigVideo())
    
    @staticmethod
    def get_local_orig_video(pconfig:cPlatformConfig):
        return os.path.join(pconfig.getWorkDir(), 
                            pconfig.getVideoProcessLclWorkDir(), 
                            pconfig.getVideoProcessOrigVideo())

'''
Web functions
'''


class cClient:
    def __init__(self, config: cPlatformConfig, target: LinuxTarget, count_exp, use_webcam=False):
        self._cfg = config
        self._trg = target
        self._count_exp = count_exp
        self._use_webcam = use_webcam

    def _create_h2load_script(self)->str:
        cmd = '''#!/bin/bash
if [[ $# -lt 11 ]]; then
    echo "Использование: $0 num_launch time_launch log_file_prefix log_dir c_num n_num t_num T_num N_num h1_str h2load_name"
    exit 1
fi

num_launch=$1
time_launch=$2
log_file_prefix=$3
log_file_dir=$4
c_num=$5
n_num=$6
t_num=$7
T_num=$8
N_num=$9
h1_str=${10}
h2load_name=${11}
standard_h2load=0
csv_out=""

if [ ! -d "$log_file_dir" ]; then
    mkdir $log_file_dir
fi

if [[ $# -gt 11 ]]; then
    standard_h2load=1
    csv_out="$log_file_dir/${12}"
    echo "count, max, min, avg" > "$csv_out"
fi 


main_logfile="$log_file_dir/$log_file_prefix.txt"
echo "" > "$main_logfile"

for (( i=1; i<=num_launch; i++ ))
do
    log_file="${log_file_prefix}_${i}.txt"
    log_file="$log_file_dir/$log_file"
    timeout -s SIGINT $time_launch bash -c "$h2load_name -c $c_num -n $n_num -t $t_num -T $T_num -N $N_num --log-file "$log_file" --h1 $h1_str >> "$main_logfile"; sleep $time_launch"
    input_file=$log_file
    if [ $standard_h2load == 1 ]
    then
        count=$(awk '$2==200{count++}END{print count}' "$input_file")
        max=$(awk 'NR==1{max=$3;min=$3;sum=0} $3>max{max=$3} $3<min{min=$3} {sum+=$3}END{print max}' "$input_file")
        min=$(awk 'NR==1{max=$3;min=$3;sum=0} $3>max{max=$3} $3<min{min=$3} {sum+=$3}END{print min}' "$input_file")
        avg=$(awk '{sum+=$3}END{print sum/NR}' "$input_file")
        echo "$count, $max, $min, $avg" >> "$csv_out"
    fi
    if [ "${13}" != "--save" ]
    then
        rm "$input_file"
    fi
done       
        '''
        return cmd

    def _create_init_script(self)->str:
        answer='#!/bin/bash\n'
        answer+="\nip r del "
        answer+=('.'.join(self._cfg.getNetworkClientHost().split('.')[:-1])) + ".0/24\n"
        answer+="\nulimit -n 60000\n"  
        return answer

    '''
    логи видео сохраняются прямо в remote!!!
    '''
    def _create_video_script(self, remote_dir)->str:
        answer = "#!/bin/bash\n"
        answer += "filename=$1\n"
        port_send = self._cfg.getPortOfAttack()
        if self._use_webcam:
            answer += "ffmpeg -f v4l2 -video_size 640x480 -i /dev/video0 -c:v h264 "
            answer += "-f mpegts udp://" + self._cfg.getNetworkWebHost() + ":" + port_send
        else:
            answer += "ffmpeg -re -i " + "" + remote_dir + "${filename} -c copy "
            answer += "-f mpegts udp://" + self._cfg.getNetworkWebHost() + ":" + port_send 
        answer += " > " + remote_dir + "sendong_log_${filename}_" + str(self._count_exp) + ".txt 2>&1\n"
        return answer

    def _run_client_load_script(self, log_prefix, remote_dir='/home/user', attack=False):
        cmd = f"nohup bash {remote_dir}/h2load.sh "
        if attack:
            time_video = 0 if not self._cfg.getUseVideo() else int(self._cfg.getTimeOfVideo())
            print(f"Time of video {time_video}")
            time_of_attack = int(self._cfg.getTimeOfAttack()) - time_video
            num_launch = time_of_attack // int(self._cfg.getLaunchTime())
            cmd+=f"{num_launch} "
            print(f'execute {num_launch} launches')
        else:
            cmd+=f"{self._cfg.getNumLaunchNormal()} "
            print(f'execute {self._cfg.getNumLaunchNormal()} launches')
        cmd += f"{self._cfg.getLaunchTime()} {log_prefix}{str(self._count_exp)} "
        cmd += f"{remote_dir}/{self._cfg.getLoadLogDir()} {self._cfg.getCountOfClient()} {self._cfg.getCountOfClient()} {self._cfg.getThreadsClient()} "
        cmd += f"{self._cfg.getTimeoutClient()} {self._cfg.getTimeoutClient()} "
        if (self._cfg.getPortOfAttack() == "80"):
            cmd += "http://"
        elif(self._cfg.getPortOfAttack() == "443"):
            cmd += "https://"
        cmd += self._cfg.getNetworkWebHost()+":"
        cmd += self._cfg.getPortOfAttack()+"/"+self._cfg.getWebHtml()
        cmd += f" {self._cfg.getLoadUtilPath()} "
        cmd += f" {log_prefix}{self._count_exp}{self._cfg.getLoadLogCsv()}.csv "
        cmd += "--save" if self._cfg.getLoadSaveInterLogs() else ""
        print(f"'{cmd}'")
        self._trg.execute(cmd, check_exit_code=True)

    def _create_script(self, script, local, remote):
        with open(local, "w") as tmp_file:
            tmp_file.write(script)
        self._trg.push(local, remote)
        self._trg.execute("chmod 777 " + remote)        

    def init_script(self, ttl=200)->str:
        local_init_path = self._cfg.getWorkDir()+"scripts/client.sh"
        local_init_video_path = self._cfg.getWorkDir()+"scripts/video_send.sh"
        local_init_h2load_path = self._cfg.getWorkDir()+"scripts/h2load.sh"
        remote_dir = '/home/user/'
        remote_script_path = remote_dir + 'client.sh'
        remote_video_script_path = remote_dir + 'video_send.sh'
        remote_h2load_script_path = remote_dir + 'h2load.sh'
        print("Connecting to client machine...")
        self._trg.connect(timeout=ttl,check_boot_completed=True)
        # create init script
        answer = self._create_init_script()  
        print('Create init client script...')
        self._create_script(answer, local_init_path, remote_script_path)
        # create video script
        answer = self._create_video_script(remote_dir)
        print('Create video client script...')
        self._create_script(answer, local_init_video_path, remote_video_script_path)
        # create h2load script
        answer = self._create_h2load_script()
        print('Create h2load client script...')
        self._create_script(answer, local_init_h2load_path, remote_h2load_script_path)

    def _send_video(self, web:cWeb, prefix_save:str):
        web.start_video_receive(prefix_save+str(self._count_exp))
        self.start_send_script()
        print('Stop receive on web...')
        web.stop_video_script()
      
    def start_script(self, attack_ended, attack_started, test_before_attack, web:cWeb):
        print("Video sending " + ("use." if self._cfg.getUseVideo() else "don`t use"))
        #self._trg.execute("echo "" > /home/user/client_log_"+str(self._count_exp)+".txt")
        print('Config ip table on client...')
        cmd="nohup bash /home/user/client.sh"
        self._trg.execute(cmd, check_exit_code=False)
        
        #self._trg.execute('echo "" >  ')
        # send video before attack
        if self._cfg.getUseVideo():
            print('Send video before attack...')
            self._send_video(web, 'video_before_attack')

        print("Start h2load before attack...")
        self._run_client_load_script(log_prefix=self._cfg.getLoadLogPrefix()[0], 
                                     remote_dir=self._cfg.getClientWorkDir(), attack=False)

        test_before_attack.set()
        while not attack_started.is_set():
            continue

        if self._cfg.getUseVideo():
            print('Send video during attack...')
            self._send_video(web, 'video_during_attack')
 
        print("Start h2load during the attack...")
        self._run_client_load_script(log_prefix=self._cfg.getLoadLogPrefix()[1], 
                                     remote_dir=self._cfg.getClientWorkDir(), attack=True)

        # after attack
        if self._cfg.getUseVideo():
            print('Send video after attack...')
            self._send_video(web, 'video_after_attack')

        print("Start h2load after attack...")
        self._run_client_load_script(log_prefix=self._cfg.getLoadLogPrefix()[2], 
                                     remote_dir=self._cfg.getClientWorkDir(),attack=False)

        #print("Downloading videos from web...")
        #web.load_videos("./out_videos/")

        print("Downloading out from client...")
        self._download_remotelogs()
        reboot(self)


    def _download_remotelogs(self):
        remote_dir = os.path.join(self._cfg.getClientWorkDir(),
                                      self._cfg.getLoadLogDir())
        local_dir = os.path.join(self._cfg.getWorkDir(),
                                     "outs/",
                                     self._cfg.getVectorOfAttack(),
                                     self._cfg.getLoadLogDir())
        for prefix in self._cfg.getLoadLogPrefix():
            remote_txt = os.path.join(remote_dir, f"{prefix}{str(self._count_exp)}.txt")
            local_txt = os.path.join(local_dir, f"{prefix}{str(self._count_exp)}.txt")
            remote_csv = os.path.join(remote_dir, f"{prefix}{self._count_exp}{self._cfg.getLoadLogCsv()}.csv")
            local_csv = os.path.join(local_dir, f"{prefix}{self._count_exp}{self._cfg.getLoadLogCsv()}.csv")
            self._trg.pull(remote_csv, local_csv)
            self._trg.pull(remote_txt, local_txt)

    def _clear_dir(self):
        cmd = '''
if [ ! -d "$log_file_dir" ]; then
    mkdir $log_file_dir
else
    rm -f "$log_file_dir"/*
fi
        '''
        self._trg.execute(cmd)


    def load_video(self):
        local_path = self._cfg.getWorkDir() + self._cfg.getVideoProcessLclWorkDir() + self._cfg.getVideoProcessOrigVideo();
        remote_path = '/home/user/' + self._cfg.getVideoProcessOrigVideo()
        self._trg.pull(remote_path, local_path)

    def send_video(self):
        local_path = self._cfg.getWorkDir() + self._cfg.getVideoProcessLclWorkDir() + self._cfg.getVideoProcessOrigVideo();
        remote_path = '/home/user/' + self._cfg.getVideoProcessOrigVideo()
        self._trg.push(local_path, remote_path)

    def parse_out(self):
        avg_dict = dict()
        avg_dict.update({'time': []})
        avg_dict.update({'reqs': []})
        avg_dict.update({'speed': []})
        avg_dict.update({'succeeded': []})
        dict_exp = []
        #parse all outputs
        for count_exp in range(0,int(self._cfg.getCountOfTests())):
            dict_exp.append({})
            with open(self._cfg.getWorkDir()+"outs/" + self._cfg.getVectorOfAttack() + \
                       "/out_client_"+str(count_exp+1)+".txt",'r') as tmpFile:
                content = list(filter(None, tmpFile.read().split('\n')))
                dict_exp[count_exp].update({'time': []})
                dict_exp[count_exp].update({'reqs': []})
                dict_exp[count_exp].update({'speed': []})
                dict_exp[count_exp].update({'succeeded': []})
                for el in content:
                    time = get_time(el)
                    reqs = get_reqs(el)
                    speed = get_speed(el)
                    succeeded = get_succeeded(el)
                    if time:
                        dict_exp[count_exp]['time'].append(time)
                    if reqs:
                        dict_exp[count_exp]['reqs'].append(reqs)
                    if speed:
                        dict_exp[count_exp]['speed'].append(speed)
                    if succeeded != None:
                        dict_exp[count_exp]['succeeded'].append(succeeded)
                print("Out №%d from client: \n" % (count_exp+1), dict_exp[count_exp], "\n")
        #average to avg dict
        #pprint.pprint(dict_exp)

        '''
            use only tests outs with equal len
        '''
        time_lengths = list(map(lambda x: len(x['time']), dict_exp))
        most_common_time_length = max(time_lengths, key=time_lengths.count)
        count_with_most_common = time_lengths.count(most_common_time_length)

        for number_measurement in range(0, most_common_time_length):
            for key in ['time','reqs', 'speed', 'succeeded']:
                sum = 0
                for count_exp in range(0,int(self._cfg.getCountOfTests())):
                    if len(dict_exp[count_exp][key]) == most_common_time_length:
                      sum+=float(dict_exp[count_exp][key][number_measurement])
                avg_dict[key].append(sum/count_with_most_common)
        #copy time
        print("Average from client: \n", avg_dict)
        return avg_dict, count_with_most_common
    
    def start_send_script(self):
        #cmd="nohup bash /home/user/video_send.sh " + '>> /home/user/video_send_log_' + name + '.txt 2>&1' + " &"
        cmd=f"nohup bash /home/user/video_send.sh {self._cfg.getVideoProcessOrigVideo()} &"
        print(cmd)
        self._trg.execute(cmd, check_exit_code=False)

    def stop_h2load(self):
        cmd = '(test -f /home/user/h2load_pid) && (echo "try delete pid") && '
        cmd += '(kill $(cat /home/user/h2load_pid))'
        self._trg.execute(cmd, check_exit_code=False)        

    def parse_out():
        pass



def get_time(string):
    index_time = string.find("finished in ")
    if not index_time:
        index_comma = string.find(",", index_time)
        if string[index_comma-2].isalpha():
            #ms to sec
            msec = string[index_time+len("finished in "):index_comma-2]
            return str(float(msec) / 1000)
        else:
            return string[index_time+len("finished in "):index_comma-1]

def get_reqs(string):
    index_time = string.find("finished in ")
    if not index_time:
        index_reqs = string.find(",", index_time)+2 # +2 for ", "
        index_space = string.find(" ", index_reqs)
        return string[index_reqs:index_space]


def get_speed(input_string):
    index_time = input_string.find("finished in ")
    if not index_time:
        match = re.search(r"(\d+(\.\d+)?)\s*(\w+)/s$", input_string)
        if match:
            speed = float(match.group(1))
            unit = match.group(3)
            if unit == 'B':
                speed /= 1024 * 1024
            elif unit == 'KB':
                speed /= 1024
            elif unit == 'G':
                speed *= 1024
            return speed
        else:
            return None

def get_succeeded(string):
    index_done = string.find("done, ")
    if (index_done != -1):
        index_succ = string.find("succeeded", index_done)
        return int(string[index_done+6:index_succ-1])

def reboot(self:cClient):
        print("Client machine:rebooting...")
        self._trg.reboot(connect=False)