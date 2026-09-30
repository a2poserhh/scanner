# Scanner

A Python CLI for checking TCP ports, pinging hosts, and discovering responsive hosts in a subnet. It uses the Python standard library; ping and subnet discovery also need a Linux-compatible `ping` executable and permission to send ICMP traffic.

## Usage

Run these commands from the repository root:

```bash
python3 main.py --help
python3 main.py scanport 127.0.0.1 8000
python3 main.py scan 127.0.0.1
python3 main.py ping 127.0.0.1
python3 main.py subnet 127.0.0.0/30
```

Aliases: `sP` = `scanport`, `sn` = `scan`, `p` = `ping`, and `s` = `subnet`. Single-port scans require a port between 1 and 65535. Subnets require an aligned network address, such as `127.0.0.0/30`.

## Results and logging

Commands return JSON on standard output. Timestamped logs go to standard error and append to `data.log` in the working directory. Each command logs its target and completion time.

- TCP scans check ports 1–1024 with 100 workers. Results include sorted open ports, closed/error counts, error details, and `elapsed_seconds`.
- Single-port results include the port, status, error, and connection time.
- Ping results include whether the host responded and elapsed time. Logs distinguish no response from missing executables, timeouts, and permission errors.
- Subnet results include the hosts checked, responding hosts, outcome counts, and elapsed time.

Save results separately from diagnostics:

```bash
python3 main.py scan 127.0.0.1 > results.json 2> scan.log
```

## Why these changes

Timing uses `time.perf_counter()` so system clock adjustments cannot distort elapsed durations. Summary counts make incomplete or error-heavy scans visible. Only connection refusal counts as a closed port; other socket failures are errors. JSON makes results reusable, and separate log output keeps saved JSON valid. Logging setup avoids duplicate entries when called again. The missing `scanport` port argument and alternate subnet dispatch were also fixed.

## Test from your terminal

From the repository root, paste:

```bash
python3 -m unittest discover -s tests -p test_results.py -v
```

All 11 tests passed with Python 3.12.14. The suite checks real loopback TCP connections, a complete CLI scan, JSON results, timing, totals, invalid inputs, ping diagnostics, subnet summaries, and duplicate log prevention. Port 1024 must be free for the full-scan test; it normally requires no elevated privileges. Ping/subnet response tests use simulated responses, so ICMP permission is not needed to run the suite. The older `tests/test.py` is an exploratory script with broken imports; the command above selects the maintained suite.

## Limits

TCP scanning uses IPv4; subnet scanning is sequential. This cloud runtime currently denies ICMP, so ping/subnet discovery needs runtime permission before it can succeed. An `alive: false` result or a "not detected" host does not prove the host is down—check the diagnostic logs.

CLI output is now JSON. `scan()` and `subnet_scan()` return dictionaries; `check_port()` retains its tuple and `is_alive()` its boolean. Exit status 0 means a result was produced, including closed ports or unsuccessful pings; inspect the result and logs. Invalid CLI arguments exit with status 2, and invalid subnet input exits with status 1.
