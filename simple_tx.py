#!/usr/bin/env python3
"""Transmit a single LoRa packet on the MeshCore US/Canada channel.

Usage:
    python examples/simple_tx.py [PORT] [MESSAGE]
"""

import sys

import donglora as dl
from _common import MESHCORE_US

port = None
message = "Hello from DongLoRa!"

args = sys.argv[1:]
if args and not args[0].startswith("/dev"):
    message = " ".join(args)
elif args:
    port = args[0]
    if len(args) > 1:
        message = " ".join(args[1:])

with dl.connect(port, config=MESHCORE_US) as d:
    td = d.tx(message.encode())
    print(f"Sent {message!r} ({td.airtime_us} µs on air)")
