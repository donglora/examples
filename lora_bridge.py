#!/usr/bin/env python3
"""Two-way LoRa bridge over TCP — relay packets between two DongLoRa dongles
across any IP network (LAN, Tailscale, WireGuard, internet).

Architecture::

    [Radio A] <-USB-> [DongLoRa A] <-TCP-> [DongLoRa B] <-USB-> [Radio B]

Usage::

    # Machine A (server):
    python examples/lora_bridge.py --mode server --port 9100

    # Machine B (client):
    python examples/lora_bridge.py --mode client --host machineA --port 9100

Both sides open a local DongLoRa, listen for incoming LoRa packets,
forward them over TCP to the peer, and transmit any TCP-arriving
bytes over the air. The Dongle class handles keepalive + recovery
internally, so no extra bookkeeping is needed here.
"""

import argparse
import socket
import struct
import sys
import threading
import time

import donglora as dl
from _common import MESHCORE_US


def tcp_send(sock: socket.socket, payload: bytes):
    """Send a length-prefixed message over TCP."""
    sock.sendall(struct.pack("<I", len(payload)) + payload)


def tcp_recv(sock: socket.socket) -> bytes | None:
    """Receive a length-prefixed message from TCP. Returns None on disconnect."""
    header = b""
    while len(header) < 4:
        chunk = sock.recv(4 - len(header))
        if not chunk:
            return None
        header += chunk
    length = struct.unpack("<I", header)[0]
    if length > 65536:
        return None
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def radio_to_tcp(d: dl.Dongle, sock: socket.socket):
    """Thread: forward LoRa RX packets to TCP."""
    for pkt in d.rx(timeout=1.0):
        try:
            sf = d.config.sf if isinstance(d.config, dl.LoRaConfig) else 7
            min_snr = -2.5 * (sf - 4)
            if pkt.snr_db < -32 or pkt.snr_db > 32:
                grade = "INVALID"
            elif pkt.snr_db < min_snr:
                grade = "UNRELIABLE"
            elif pkt.snr_db < min_snr + 3:
                grade = "MARGINAL"
            else:
                grade = "GOOD"
            if grade in ("INVALID", "UNRELIABLE"):
                print(
                    f"  RX drop len:{len(pkt.data):3d}  "
                    f"rssi:{pkt.rssi_dbm:.1f}dBm  snr:{pkt.snr_db:.1f}dB  [{grade}]"
                )
                continue
            tag = f"  [{grade}]" if grade == "MARGINAL" else ""
            print(
                f"  RX→TCP  len:{len(pkt.data):3d}  "
                f"rssi:{pkt.rssi_dbm:.1f}dBm  snr:{pkt.snr_db:.1f}dB{tag}"
            )
            tcp_send(sock, pkt.data)
        except OSError as exc:
            print(f"  [radio→tcp error: {exc}]")
            return


def tcp_to_radio(d: dl.Dongle, sock: socket.socket):
    """Thread: forward TCP packets to LoRa TX."""
    while True:
        try:
            payload = tcp_recv(sock)
            if payload is None:
                print("  [TCP disconnected]")
                return
            print(f"  TCP→TX  len:{len(payload):3d}")
            d.tx(payload)
        except (OSError, dl.DongloraError) as exc:
            print(f"  [tcp→radio error: {exc}]")
            return


def main():
    parser = argparse.ArgumentParser(description="DongLoRa two-way LoRa bridge over TCP")
    parser.add_argument("--mode", choices=["server", "client"], required=True)
    parser.add_argument("--host", default="localhost", help="Remote host (client mode)")
    parser.add_argument("--port", type=int, default=9100, help="TCP port")
    parser.add_argument("--serial", default=None, help="Serial port (auto-detect if omitted)")
    args = parser.parse_args()

    try:
        if args.mode == "server":
            print(f"Listening on port {args.port}...")
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("0.0.0.0", args.port))
            srv.listen(1)
            sock, addr = srv.accept()
            print(f"Connected from {addr}")
            srv.close()
        else:
            print(f"Connecting to {args.host}:{args.port}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((args.host, args.port))
            print("Connected")

        with dl.connect(args.serial, config=MESHCORE_US) as d:
            print(f"Radio ready on {d.config.freq_hz / 1e6:.3f} MHz — bridging packets\n")
            t1 = threading.Thread(target=radio_to_tcp, args=(d, sock), daemon=True)
            t2 = threading.Thread(target=tcp_to_radio, args=(d, sock), daemon=True)
            t1.start()
            t2.start()
            try:
                while t1.is_alive() and t2.is_alive():
                    time.sleep(0.5)
            except KeyboardInterrupt:
                pass
        print("\nBridge stopped.")

    except KeyboardInterrupt:
        print("\nInterrupted.")
    except dl.DongloraError as exc:
        print(f"\nDevice error: {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"\nNetwork error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
