#!/usr/bin/env python3
"""Verify the dongle applies ``LoRaConfig.sync_word`` to the radio.

Two roles. Run on TWO SEPARATE PHYSICAL DONGLES (not the same dongle
shared via donglora-mux — a single chip can only hold one sync word at
a time, and the mux delivers local TX back to other sessions as
LOCAL_LOOPBACK events that bypass the chip's sync filter). Pass an
explicit port path to each invocation so neither side discovers the
mux socket:

    # Dongle A — pin to one sync word, listen:
    python examples/sync_word_test.py --role rx /dev/ttyACM0 [--sync 0x5464]

    # Dongle B — rotate through several sync words, transmitting on each:
    python examples/sync_word_test.py --role tx /dev/ttyACM1

Expected behavior with the firmware fix:
    RX hears ONLY the cycles whose sync word matches its own
    (one packet per rotation pass through SYNC_WORDS), and packets
    have realistic RSSI / SNR (not 0.0 / 0.0).

Without the fix:
    RX hears every transmission regardless of which sync word the TX
    side configured — the firmware was silently ignoring the field
    and leaving the SX126x on the boot-time default 0x1424.

The default RX sync word (0x5464) is deliberately off the MeshCore
(0x1424) and LoRaWAN-public (0x3444) values so the test isn't polluted
by ambient mesh traffic. The RX role drops `LOCAL_LOOPBACK` events
defensively so accidental mux sharing fails loud (zero packets) rather
than printing misleading "all sync words received" output.
"""

import argparse
import dataclasses
import time

import donglora as dl
from _common import MESHCORE_US

# SX126x register-encoded sync words. Each is (hi << 8) | lo where
# [hi, lo] = convert_sync_word(byte) for the listed underlying byte:
#   byte 0x12 → 0x1424   (LoRa "private" — MeshCore default)
#   byte 0x34 → 0x3444   (LoRaWAN "public")
#   byte 0x56 → 0x5464
#   byte 0x78 → 0x7484
#   byte 0xAB → 0xA4B4
#   byte 0xCD → 0xC4D4
SYNC_WORDS = [0x1424, 0x3444, 0x5464, 0x7484, 0xA4B4, 0xC4D4]
TX_PAUSE_S = 1.5

parser = argparse.ArgumentParser(description="Sync-word verification test")
parser.add_argument("--role", choices=["tx", "rx"], required=True)
parser.add_argument(
    "--sync",
    type=lambda x: int(x, 0),
    default=0x5464,
    help="(rx) sync word to pin to, e.g. 0x5464 (default; avoids MeshCore noise)",
)
parser.add_argument("port", nargs="?", help="Serial port (auto-detect if omitted)")
args = parser.parse_args()

if args.role == "tx":
    with dl.connect(args.port, config=MESHCORE_US) as d:
        print(
            f"TX: rotating {len(SYNC_WORDS)} sync words, "
            f"{TX_PAUSE_S}s between (Ctrl+C to stop)\n"
        )
        try:
            cycle = 0
            while True:
                for sw in SYNC_WORDS:
                    cfg = dataclasses.replace(MESHCORE_US, sync_word=sw)
                    d.set_config(cfg)
                    msg = f"cycle={cycle} sync=0x{sw:04X}"
                    td = d.tx(msg.encode())
                    print(
                        f"  TX sync=0x{sw:04X}  {msg!r}  ({td.airtime_us} µs)"
                    )
                    time.sleep(TX_PAUSE_S)
                cycle += 1
        except KeyboardInterrupt:
            print("\nDone.")
else:
    sw = args.sync
    cfg = dataclasses.replace(MESHCORE_US, sync_word=sw)
    with dl.connect(args.port, config=cfg) as d:
        print(f"RX: pinned to sync=0x{sw:04X} (Ctrl+C to stop)")
        print("Only matching-sync-word transmissions should arrive.\n")
        try:
            for pkt in d.rx():
                if pkt.origin != dl.RxOrigin.OTA:
                    # Drop mux-injected local-loopback events. They
                    # arrive without going through the chip's sync
                    # filter and would falsely "match" every sync
                    # word the TX side rotates through.
                    continue
                text = pkt.data.decode("utf-8", errors="replace")
                print(
                    f"  RX: {text!r}  RSSI:{pkt.rssi_dbm:.1f}dBm  "
                    f"SNR:{pkt.snr_db:.1f}dB"
                )
        except KeyboardInterrupt:
            print("\nDone.")
