#!/bin/bash
filename=$1
ffmpeg -y -i udp://192.168.56.77:1234 -c copy "/home/user/save_videos/${filename}.mkv"  > /home/user/logs_video/receive_log_${filename}.txt 2>&1 &
echo $! > /home/user/ffmpeg_pid