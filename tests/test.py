import ipaddress
from func import validate_ip, checking_host
import ipaddress

joe = ipaddress.ip_interface('192.168.1.217/24')
bob = ipaddress.ip_network('192.168.1.217/24', strict=False)
john = ipaddress.ip_address('192.168.1.217')
test = ipaddress.ip_network('192.168.1.0/24')

addr6 = ipaddress.ip_address('2001:db8::1')
addr4 = ipaddress.ip_address('192.0.2.1')




def print_test():
    print(joe.version)
    print(joe.network)
    print(bob.num_addresses)
    print(test.num_addresses)
#these can be combined but not rn

def unusable_port_scan():
    net4 = ipaddress.ip_network('192.168.1.217/24', strict=False)
    for x in net4.hosts():
        print(x)
#dont run this by itself, i need to build something around this because
#i dont see why i would run it sol

def mask_scan():
    mask4 = ipaddress.ip_network('192.168.1.0/24')
    print(mask4.netmask)

def explode():
    addr6.exploded
    #cant use rn but vice versa for compress
    #more or less IP info

#net4[1] learn how to make a list(i assume an array)

#for later
#for address in network:
    #do something

if addr4 in ipaddress.ip_network('192.0.2.0/24'):
    print("true")
else:
    print("false")

if addr4 in ipaddress.ip_network('192.0.3.0/24'):
    print("true")
else:
    print("false")

mask_scan()

t5 = ipaddress.ip_network('172.168.1.0/24').subnets()

#for net in t5:
#    print(net)

network = ipaddress.ip_network('192.168.1.0/24')

#for host in network.hosts():
#    print(host)

print(network.hosts())

for something in network.hosts():
    print(validate_ip(something))




