#import SubnetTree

#t = SubnetTree.SubnetTree()
#t["10.1.0.0/16"] = "Network 1"
#t["10.1.42.0/24"] = "Network 1, Subnet 42"


t1 =ipaddress.ip_interface('192.168.1.217/24')
t2 = ipaddress.ip_network('172.168.1.0/24', strict=False)
t3 = ipaddress.ip_address('192.168.1.217')
#now i have more context, this is telling how much info is attached to it
#t2 has the most info as we are giving the IP and saying "you do the rest"

#print(t1.ip) # attribute
#print(t1.network) # attribute

#print(t2.network_address) # attribute
#print(t2.broadcast_address) # attribute
#print(t2.num_addresses) # attribute

#t2.host() #method

#t4 = ipaddress.ip_address("172.168.1.0").reverse_pointer

#print(t4)

#for host in t2.hosts():
#    print(host)
