import ipaddress
import socket
import argparse


def validate_ip(target):
    try:
        ip = ipaddress.ip_address(target)
        print(f"Valid IP: {ip}")
    except ValueError:
        print("Invalid IP address")

def checking_host(host):
       try:
              ip = socket.gethostbyname(host)
              print(f"{host} resolves to {ip}")
       except socket.gaierror:
              print("invalid host name")

def main():


       parser = argparse.ArgumentParser()
        #object to call the parser easier

       parser.add_argument("command") #does what it says, i want to add a command.
       parser.add_argument("target") #i need to what this is doing, this was explained very well after asking

       args = parser.parse_args() #if you know what parsing is then its in the name

       if args.command == "validate":
              validate_ip(args.target) 
       elif args.command == "resolve":
              checking_host(args.target)
       else:
              print("wtf did you type brah")
      
if __name__ == "__main__":
    main()