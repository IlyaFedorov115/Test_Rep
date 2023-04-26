import time
from platform_config import cPlatformConfig
from devlib import LinuxTarget
from web import cWeb
import pprint
import re


class cClient:
    def __init__(self, config: cPlatformConfig, target: LinuxTarget, count_exp, use_webcam=False):
        self._cfg = config
        self._trg = target
        self._count_exp = count_exp
        self._use_webcam = use_webcam

    def init_script(self, ttl=200)->str:
        local_init_path = self._cfg.getWorkDir()+"scripts/client.sh"
        local_init_video_path = self._cfg.getWorkDir()+"scripts/video_send.sh"

        remote_dir = '/home/user/'
        remote_script_path = remote_dir + 'client.sh'
        remote_video_script_path = remote_dir + 'video_send.sh'

        #create script
        answer='#!/bin/bash\n'
        answer+="\nip r del "
        answer+=('.'.join(self._cfg.getNetworkClientHost().split('.')[:-1])) + ".0/24\n"
        print('====Del addres ', answer)
        answer+="\nulimit -n 60000\n"
        answer+="h2load -c "+self._cfg.getCountOfClient()+" -n "+self._cfg.getCountOfClient()
        answer+=" -t "+self._cfg.getThreadsClient()+" -T "+self._cfg.getTimeoutClient()
        answer+=" -N "+self._cfg.getTimeoutClient()
        answer+=" --h1 "
        if (self._cfg.getPortOfAttack() == "80"):
            answer+="http://"
        elif(self._cfg.getPortOfAttack() == "443"):
            answer+="https://"
        answer+=self._cfg.getNetworkWebHost()+":"
        answer+=self._cfg.getPortOfAttack()+"/"+self._cfg.getWebHtml()
        answer+=" >> /home/user/client_log_"+str(self._count_exp)+".txt &\n"

        answer+="echo $! > /home/user/h2load_pid"
        with open(local_init_path,'w') as tmp_file:
            tmp_file.write(answer)


        #push and chmod script
        print(local_init_path)
        print(remote_script_path)
        print("Connecting to client machine...")
        self._trg.connect(timeout=ttl,check_boot_completed=True)
        self._trg.push(local_init_path, remote_script_path)
        self._trg.execute("chmod 777 " + remote_script_path)

        # create video script
        answer = "#!/bin/bash\n"
        answer += "filename=$1\n"
        port_send = self._cfg.getPortOfAttack()
        port_send = "1234"
        if self._use_webcam:
            answer += "ffmpeg -f v4l2 -video_size 640x480 -i /dev/video0 -c:v h264 "
            answer += "-f mpegts udp://" + self._cfg.getNetworkWebHost() + ":" + port_send
        else:
            answer += "ffmpeg -re -i " + "" + remote_dir + "${filename} -c copy "
            answer += "-f mpegts udp://" + self._cfg.getNetworkWebHost() + ":" + port_send 

        # изменил чтобы не фоново, убрал &
        answer += " > /home/user/sendong_log_${filename}_" + str(self._count_exp) + ".txt 2>&1\n"

        with open(local_init_video_path, "w") as tmp_file:
            tmp_file.write(answer)

        # push and chmod video script
        self._trg.push(local_init_video_path, remote_video_script_path)
        self._trg.execute("chmod 777 " + remote_video_script_path)
        

    def start_script(self, attack_ended, attack_started, test_before_attack, web:cWeb):
        self._trg.execute("echo "" > /home/user/client_log_"+str(self._count_exp)+".txt")
        cmd="nohup bash /home/user/client.sh"
        print(cmd)

        # send video before attack
        web.start_video_receive('video_before_attack'+str(self._count_exp))
        print('Send video before attack...')
        self.start_send_script()
        print('Stop receive on web...')
        web.stop_video_script()


        for i in range(1,4):
            print("%d start h2load before attack..." %i)
            self._trg.execute(cmd, check_exit_code=False)
        
        test_before_attack.set()

        while not attack_started.is_set():
            continue

        web.start_video_receive('video_during_attack'+str(self._count_exp))
        print('Send video during attack...')
        self.start_send_script()
        print('Stop receive on web...')
        web.stop_video_script()

        count = 1
        while not attack_ended.is_set():
            print("%d start h2load during the attack..." %count)
            self._trg.execute(cmd, check_exit_code=False)
            count+=1

        self.stop_h2load()

        # after attack
        web.start_video_receive('video_after_attack'+str(self._count_exp))
        print('Send video after attack')
        self.start_send_script()
        web.stop_video_script()


        for i in range(1,4):
            print("%d start h2load after attack..." %i)
            self._trg.execute(cmd, check_exit_code=False)

        #print("Downloading videos from web...")
        #web.load_videos("./out_videos/")

        print("Downloading out from client...")
        self._trg.pull("/home/user/client_log_"+str(self._count_exp)+".txt", str(self._cfg.getWorkDir())+"outs/" \
                        + self._cfg.getVectorOfAttack() + "/out_client_"+str(self._count_exp)+".txt")
        reboot(self)

    def load_video(self):
        local_path = self._cfg.getWorkDir() + self._cfg.getVideoProcessLclWorkDir() + self._cfg.getVideoProcessOrigVideo();
        remote_path = '/home/user/' + self._cfg.getVideoProcessOrigVideo();
        self._trg.pull(remote_path, local_path)

    def send_video(self):
        local_path = self._cfg.getWorkDir() + self._cfg.getVideoProcessLclWorkDir() + self._cfg.getVideoProcessOrigVideo();
        remote_path = '/home/user/' + self._cfg.getVideoProcessOrigVideo();
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

