#!/usr/bin/env python3
"""Receive LoRa packets on the MeshCore US/Canada channel.

Usage:
    python examples/simple_rx.py [PORT]
"""

import sys

import donglora as dl
from _common import MESHCORE_US

port = sys.argv[1] if len(sys.argv) > 1 else None

with dl.connect(port, config=MESHCORE_US) as d:
    print(f"Listening on {d.config.freq_hz / 1e6:.3f} MHz (Ctrl+C to stop)...\n")
    try:
        for pkt in d.rx():
            print(
                f"  RSSI:{pkt.rssi_dbm:6.1f} dBm  SNR:{pkt.snr_db:5.1f} dB  "
                f"len:{len(pkt.data):3d}  {pkt.data.hex()}"
            )
    except KeyboardInterrupt:
        print("\nDone.")
