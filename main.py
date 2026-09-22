import socket
import concurrent.futures
import ipaddress
import argparse
import logging
import subprocess
import time

from datetime import datetime
from func.logger import setup_logging
from func.webport import check_port, scan, is_alive, subnet_scan

start_time = datetime.now()
logger = logging.getLogger(__name__)

def main():

    setup_logging()

    parser = argparse.ArgumentParser()#object to call the parser easier
    subparser = parser.add_subparsers(
        dest="command",
        required=True,
    )

    port_scan_parser = subparser.add_parser("scanport", aliases=["sP"])
    port_scan_parser.add_argument("target")
    port_scan_parser.set_defaults(func=check_port)

    ping_parser = subparser.add_parser("ping", aliases=["p"])
    ping_parser.add_argument("target")
    ping_parser.set_defaults(func=is_alive)

    scan_parser = subparser.add_parser("scan", aliases=["sn"])
    scan_parser.add_argument("target")
    scan_parser.set_defaults(func=scan)

    subnet_parser = subparser.add_parser("subnet", aliases=["s"])
    subnet_parser.add_argument("target")
    subnet_parser.set_defaults(func=subnet_scan)

    args = parser.parse_args()
    result = args.func(args.target)
    print(result)



if __name__ == "__main__":
    main()