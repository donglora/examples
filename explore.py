#!/usr/bin/env python3
"""Probe a DongLoRa device: print capabilities, then TX + RX once.

Configures the radio for the MeshCore US/Canada channel so the TX
probe is audible to other MeshCore nodes on the same band.

Usage:
    python examples/explore.py [PORT]
"""

import sys
import time

import donglora as dl
from _common import MESHCORE_US


def describe_info(info: dl.Info) -> None:
    chip = info.chip.name if isinstance(info.chip, dl.RadioChipId) else f"0x{info.chip:04X}"
    print(f"  Protocol:  DongLoRa Protocol v{info.proto_major}.{info.proto_minor}")
    print(f"  Firmware:  v{info.fw_major}.{info.fw_minor}.{info.fw_patch}")
    print(f"  Chip:      {chip}")
    print(f"  Freq:      {info.freq_min_hz / 1e6:.1f} - {info.freq_max_hz / 1e6:.1f} MHz")
    print(f"  TX power:  {info.tx_power_min_dbm}..{info.tx_power_max_dbm} dBm")
    print(f"  Max pkt:   {info.max_payload_bytes} bytes")
    print(f"  SF range:  {info.supported_sf()}")
    print(f"  MCU UID:   {info.mcu_uid.hex()}")
    caps = []
    if info.supports(dl.Capability.LORA):
        caps.append("LoRa")
    if info.supports(dl.Capability.FSK):
        caps.append("FSK")
    if info.supports(dl.Capability.CAD_BEFORE_TX):
        caps.append("CAD")
    print(f"  Features:  {', '.join(caps) or 'none advertised'}")


port = sys.argv[1] if len(sys.argv) > 1 else None

with dl.connect(port, config=MESHCORE_US) as d:
    print("── GET_INFO ──")
    describe_info(d.info)

    cfg = d.config
    print(
        f"\n── Radio configured: {cfg.freq_hz / 1e6:.3f} MHz  "
        f"SF{cfg.sf}  BW{cfg.bw.khz:g}kHz  "
        f"sync=0x{cfg.sync_word:04X}  {cfg.tx_power_dbm} dBm ──"
    )

    print("\n── TX ──")
    td = d.tx(b"hello from explore.py")
    print(
        f"  result={td.result.name}  airtime_us={td.airtime_us}  "
        f"(~{td.airtime_us / 1000:.1f} ms on air)"
    )

    print("\n── RX (5 s window) ──")
    start = time.monotonic()
    any_rx = False
    for pkt in d.rx(timeout=0.25):
        any_rx = True
        print(
            f"  pkt: rssi={pkt.rssi_dbm:.1f}dBm snr={pkt.snr_db:.1f}dB "
            f"len={len(pkt.data)} origin={pkt.origin.name}"
        )
        if time.monotonic() - start > 5:
            break
    if not any_rx:
        print("  (no packets received — try pairing with ping_pong.py --role tx)")

print("\nDone.")
