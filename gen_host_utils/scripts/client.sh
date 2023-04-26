#!/bin/bash

ip r del 192.168.56.0/24

ulimit -n 60000
h2load -c 100 -n 100 -t 2 -T 2 -N 2 --h1 http://192.168.56.77:80/1,5MB.html >> /home/user/client_log_1.txt &
echo $! > /home/user/h2load_pid