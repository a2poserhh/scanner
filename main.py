import argparse
import json
import logging
import time

from func.logger import setup_logging
from func.webport import check_port, scan, is_alive, subnet_scan

logger = logging.getLogger(__name__)

def port_number(value):
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("port must be an integer")
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port

def main():
    parser = argparse.ArgumentParser()#object to call the parser easier
    subparser = parser.add_subparsers(
        dest="command",
        required=True,
    )

    port_scan_parser = subparser.add_parser("scanport", aliases=["sP"])
    port_scan_parser.add_argument("target")
    port_scan_parser.add_argument("port", type=port_number)
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
    setup_logging()
    started = time.perf_counter()
    logger.info("Starting %s for %s", args.command, args.target)
    try:
        if args.func is check_port:
            port, status, error, elapsed = check_port(args.target, args.port)
            result = {
                "target": args.target, "port": port, "status": status,
                "error": error, "elapsed_seconds": elapsed,
            }
            logger.log(
                logging.ERROR if error else logging.INFO,
                "%s port %s: %s%s", args.target, port, status,
                f" ({error})" if error else "",
            )
        elif args.func is is_alive:
            result = {
                "target": args.target, "alive": is_alive(args.target),
                "elapsed_seconds": time.perf_counter() - started,
            }
        else:
            result = args.func(args.target)
    except (ValueError, OSError) as error:
        logger.error(
            "%s for %s failed after %.4fs: %s",
            args.command, args.target, time.perf_counter() - started, error,
        )
        return 1
    logger.info(
        "%s for %s completed in %.4fs",
        args.command, args.target, time.perf_counter() - started,
    )
    print(json.dumps(result, indent=2))
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
