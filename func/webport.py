import socket
import concurrent.futures
import ipaddress
import argparse
import errno
import logging
import os
import subprocess
from func.logger import setup_logging
import time

logger = logging.getLogger(__name__)

def check_port(target, port):
    start_ptime = time.perf_counter()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
        elapsed = time.perf_counter() - start_ptime
        if result == 0:
            return (port, "open", None, elapsed)
        if result == errno.ECONNREFUSED:
            return (port, "closed", None, elapsed)
        return (port, "error", os.strerror(result), elapsed)
    except OSError as e:
        elapsed = time.perf_counter() - start_ptime
        return (port, "error", str(e), elapsed)

def scan(target):
    started = time.perf_counter()
    open_ports = []
    closed_count = 0
    errors = []
    logger.info("Starting TCP scan of %s: ports 1-1024, 100 workers", target)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(check_port, target, p): p for p in range(1, 1025)}
        for future in concurrent.futures.as_completed(futures):
            port, status, err, elapsed = future.result()
            if status == "open":
                open_ports.append(port)
                logger.info("%s port %s: open (connect time: %.4fs)", target, port, elapsed)
            elif status == "error":
                errors.append({"port": port, "message": err})
                logger.error("%s port %s: %s (connect time: %.4fs)", target, port, err, elapsed)
            elif status == "closed":
                closed_count += 1

    elapsed = time.perf_counter() - started
    result = {
        "target": target,
        "ports_scanned": len(open_ports) + closed_count + len(errors),
        "open_ports": sorted(open_ports),
        "closed_count": closed_count,
        "error_count": len(errors),
        "errors": sorted(errors, key=lambda error: error["port"]),
        "elapsed_seconds": elapsed,
    }
    logger.info(
        "TCP scan of %s completed in %.4fs: %s ports checked, %s open, %s closed, %s errors",
        target, elapsed, result["ports_scanned"], len(open_ports), closed_count, len(errors),
    )
    return result

def is_alive(target):
    """Send one ping, return True if the host responds."""
    started = time.perf_counter()
    target = str(target)
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", "--", target],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        logger.error("Ping of %s failed after %.4fs: %s", target, time.perf_counter() - started, e)
        return False

    elapsed = time.perf_counter() - started
    if result.returncode not in (0, 1):
        logger.error(
            "Ping of %s failed after %.4fs (exit %s): %s",
            target, elapsed, result.returncode,
            result.stderr.strip() or result.stdout.strip() or "No diagnostic output",
        )
    else:
        logger.info(
            "Ping of %s completed in %.4fs: %s",
            target, elapsed, "alive" if result.returncode == 0 else "no response",
        )
    return result.returncode == 0

def subnet_scan(target):
    network = ipaddress.ip_network(target, strict=True)
    started = time.perf_counter()
    alive_hosts = []
    hosts_scanned = 0
    logger.info("Starting subnet scan of %s", network)
    for host in network.hosts():
        hosts_scanned += 1
        if is_alive(str(host)):
            alive_hosts.append(str(host))
            logger.info("%s is alive", host)
    elapsed = time.perf_counter() - started
    logger.info(
        "Subnet scan of %s completed in %.4fs: %s hosts checked, %s alive, %s not detected",
        network, elapsed, hosts_scanned, len(alive_hosts), hosts_scanned - len(alive_hosts),
    )
    return {
        "target": str(network),
        "hosts_scanned": hosts_scanned,
        "alive_hosts": alive_hosts,
        "alive_count": len(alive_hosts),
        "not_detected_count": hosts_scanned - len(alive_hosts),
        "elapsed_seconds": elapsed,
    }

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
    elif args.s:
        subnet_scan(args.target)

if __name__ == "__main__":
    main()
