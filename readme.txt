Installing:
apt -y update && apt -y install curl wget libcurl4 libssl-dev python3 python3-pip make cmake automake autoconf m4 build-essential
pip3 install -r requirements.txt

Running:
L4: sudo python3.10 ./start.py syn true 192.168.56.77:80 300 true
L7: sudo python3.10 ./start.py get true 192.168.56.77:80 300 10000 true