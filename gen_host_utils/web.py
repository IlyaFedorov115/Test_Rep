from platform_config import cPlatformConfig
from devlib import LinuxTarget

class cWeb:
    def __init__(self, config: cPlatformConfig, target: LinuxTarget):
        self._cfg = config
        self._trg = target
        self._video_files = []

    def init_script(self, ttl=200, use_vlc_receive=False, format_save='mkv')->str:
        local_init_path=self._cfg.getWorkDir()+"/scripts/web.sh"
        local_init_receiver_path = self._cfg.getWorkDir()+"/scripts/video_receive.sh"

        remote_dir = '/home/user/'
        remote_script_path = remote_dir + 'web.sh'
        remote_video_script_path = remote_dir + 'video_receive.sh'

        #create script
        answer='#!/bin/bash\n'
        answer+="\nip r del "
        answer+=('.'.join(self._cfg.getNetworkWebHost().split('.')[:-1])) + ".0/24\n"

        with open(local_init_path,'w') as tmp_file:
            tmp_file.write(answer)

        #push and chmod script
        print(local_init_path)
        print(remote_script_path)
        print("Connecting to web machine...")
        self._trg.connect(timeout=ttl,check_boot_completed=True)
        self._trg.push(local_init_path, remote_script_path)
        self._trg.execute("chmod 777 " + remote_script_path)

        # create video recieve script
        video_script = "#!/bin/bash\n"
        video_script += 'filename=$1\n'
        
        if use_vlc_receive:
            video_script += 'cvlc udp://@' + self._cfg.getNetworkWebHost() +':1234 :demux=dump :demuxdump-file=' + self._cfg.getVideoProcessRmtWorkDir() +'${filename}.' + format_save + ' '
        else:
            video_script += 'ffmpeg -y -i udp://' + self._cfg.getNetworkWebHost() + ':1234 -c copy "' + self._cfg.getVideoProcessRmtWorkDir() + '${filename}.' + format_save + '" '    

        video_script += " > /home/user/logs_video/receive_log_${filename}.txt 2>&1 &\n"
        video_script += "echo $! > /home/user/ffmpeg_pid"

        with open(local_init_receiver_path, "w") as tmp_file:
            tmp_file.write(video_script)

        # push and chmod video script
        self._trg.push(local_init_receiver_path, remote_video_script_path)
        self._trg.execute("chmod 777 " + remote_video_script_path)  



    def start_video_receive(self, filename):
        cmd = f"bash /home/user/video_receive.sh {filename}"
        print(cmd)
        self._trg.execute(cmd, check_exit_code=False)
        self._video_files.append(f"{filename}.mkv")

    def start_script(self):
        cmd="nohup bash /home/user/web.sh"
        print(cmd)
        self._trg.execute(cmd, check_exit_code=False)

    def stop_video_script(self):
        cmd = '(test -f /home/user/ffmpeg_pid) && (echo "try delete pid") && '
        cmd += '(kill $(cat /home/user/ffmpeg_pid)) && (rm -f /home/user/ffmpeg_pid)'
        self._trg.execute(cmd, check_exit_code=False)

    def reboot(self):
        print("Web machine:rebooting...")
        self._trg.reboot(connect=False)

    def load_videos(self):
        for video_file in self._video_files:
            remote_file_path = f"{self._cfg.getVideoProcessRmtWorkDir()}{video_file}"
            local_file_path = f"{self._cfg.getWorkDir() + self._cfg.getVideoProcessLclWorkDir() + self._cfg.getVectorOfAttack()}/{video_file}"
            self._trg.pull(remote_file_path, local_file_path)      

    def send_video(self):
        local_path = f"{self._cfg.getWorkDir()}{self._cfg.getVideoProcessLclWorkDir()}{self._cfg.getVideoProcessOrigVideo()}"
        remote_path = f"{self._cfg.getVideoProcessRmtWorkDir()}{self._cfg.getVideoProcessOrigVideo()}"
        self._trg.push(local_path, remote_path)

    def clean_videos_dir(self):
        cmd = f'rm -rf {self._cfg.getVideoProcessRmtWorkDir()}*'
        self._trg.execute(cmd, check_exit_code=False)

    # optinal methods to get statistics from web
    # without loading all videos from remote machine
    def load_remote_stat(self):
        cmd = '''#!/bin/bash
input_file=$1
format=$2
output_file=$3
work_dir=$4
prefixes=("${@:5}")
cd $work_dir
if [ ! -f $output_file ]; then
    touch $output_file
fi
echo "filename,ssim,count_packets" > $output_file
for prefix in "${prefixes[@]}"; do
    for file in "$prefix"*."$format"; do
        if [[ -f "$file" ]]; then
            ssim=$(ffmpeg -i "$input_file" -i "$file" -lavfi ssim=stats_file=ssim_log.txt -f null - 2>&1 | grep "All:" | awk -F'All:' '/All:/ {print $2}' | awk '{print $1}')
            count_packets=$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "$file" 2>/dev/null | tail -1)
            echo "$file,$ssim,$count_packets" >> $output_file
        fi
    done
done        
        '''
        local_script_path = self._cfg.getWorkDir()+"/scripts/stat.sh"
        with open(local_script_path, "w") as tmp_file:
            tmp_file.write(cmd)

        # push and chmod video script
        self._trg.push(local_script_path, "/home/user/stat.sh")
        self._trg.execute("chmod 777 " + "/home/user/stat.sh")  
        self._trg.execute(f"nohup bash /home/user/stat.sh " +
                 f"{self._cfg.getVideoProcessOrigVideo()} " +
                 f"{self._cfg.getVideoProcessFormat()} " +
                 f"{self._cfg.getVideoProcessOutCsv()} " +
                 f"{self._cfg.getVideoProcessRmtWorkDir()} " +
                 f"{' '.join(self._cfg.getVideoProcessNames())}",
                 check_exit_code=False)
        self._trg.pull(self._cfg.getVideoProcessRmtWorkDir()+self._cfg.getVideoProcessOutCsv(), f"{self._cfg.getWorkDir()+self._cfg.getVideoProcessLclWorkDir()+self._cfg.getVectorOfAttack()}/{self._cfg.getVideoProcessOutCsv()}") 
        