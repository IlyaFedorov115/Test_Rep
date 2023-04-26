#!/bin/bash
filename=$1
ffmpeg -re -i /home/user/${filename} -c copy -f mpegts udp://192.168.56.77:1234 > /home/user/sendong_log_${filename}_1.txt 2>&1
