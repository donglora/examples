#!/usr/bin/env python3
"""Two-dongle demo on the MeshCore US/Canada channel: one TX, one RX.

Usage:
    python examples/ping_pong.py --role tx [PORT]
    python examples/ping_pong.py --role rx [PORT]
"""

import argparse
import time

import donglora as dl
from _common import MESHCORE_US

parser = argparse.ArgumentParser(description="DongLoRa ping-pong demo")
parser.add_argument("--role", choices=["tx", "rx"], required=True)
parser.add_argument("port", nargs="?", help="Serial port (auto-detect if omitted)")
args = parser.parse_args()

with dl.connect(args.port, config=MESHCORE_US) as d:
    if args.role == "tx":
        print("Transmitting every 2 seconds (Ctrl+C to stop)...\n")
        try:
            seq = 0
            while True:
                msg = f"ping #{seq}"
                td = d.tx(msg.encode())
                print(f"  TX: {msg!r}  ({td.airtime_us} µs)")
                seq += 1
                time.sleep(2)
        except KeyboardInterrupt:
            print("\nDone.")
    else:
        print("Receiving (Ctrl+C to stop)...\n")
        try:
            for pkt in d.rx():
                text = pkt.data.decode("utf-8", errors="replace")
                print(f"  RX: {text!r}  RSSI:{pkt.rssi_dbm:.1f}dBm  SNR:{pkt.snr_db:.1f}dB")
        except KeyboardInterrupt:
            print("\nDone.")
