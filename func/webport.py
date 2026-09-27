import socket
import concurrent.futures
from datetime import datetime
import ipaddress
import argparse
import logging
import subprocess
from func.logger import setup_logging
import time

start_time = datetime.now()
logger = logging.getLogger(__name__)

def check_port(target, port):
    start_ptime = time.time()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
        elapsed = time.time() - start_ptime
        if result == 0:
            return (port, "open", None, elapsed)
        return (port, "closed", None, elapsed)
    except Exception as e:
        elapsed = time.time() - start_ptime
        return (port, "error", str(e), elapsed)

def scan(target):
    closed_ports = []
    start_time = datetime.now()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(check_port, target, p): p for p in range(1, 1025)}
        for future in concurrent.futures.as_completed(futures):
            port, status, err, elapsed = future.result()
            if status == "open":
                logger.info(f"port {port}: open (Connect time: {elapsed:.2f}s)")
            elif err:
                logger.error(f"port {port}: Error - {err}")
            elif status == "closed":
                closed_ports.append(port)

    end_time = datetime.now()
    total_time = end_time - start_time
    logger.info(f"Scanning completed in: {total_time}")

def is_alive(target):
    """Send one ping, return True if the host responds."""
    try:
        target = str(target)

        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", target],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return result.returncode == 0
    
    except Exception as e:
        logger.error(f"Ping failed: {e}")
        return False

def subnet_scan(target):
    network = ipaddress.ip_network(target, strict=True) 

    for host in network.hosts():
        if is_alive(str(host)):
            print(f"{host} is alive")

def main():

    setup_logging()

    parser = argparse.ArgumentParser()#object to call the parser easier
    parser.add_argument("target")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-sn", action="store_true", help="Ping scan: is the host alive?")
    group.add_argument("-sT", action="store_true", help="TCP connect scan: scan all ports")
    group.add_argument("-s","-subnet", action="store_true", help="Scan a subnet for alive hosts")

    args = parser.parse_args()

    if args.sn:
        alive = is_alive(args.target)
        logger.info(f"{args.target} is {'alive' if alive else 'not responding'}")
    elif args.sT:
        scan(args.target)

if __name__ == "__main__":
    main()