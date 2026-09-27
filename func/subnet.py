import ipaddress
from validateIP import checking_host
from webport import is_alive

network = ipaddress.ip_network('192.168.1.0/24')

for host in network.hosts():
    if is_alive(str(host)):
        print(f"{host} is alive")