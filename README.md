# DongLoRa Examples

Example scripts demonstrating the [Python client library](https://github.com/donglora/client-py).

## Running

```sh
cd examples
just rx                     # receive packets
just tx                     # transmit a packet
just ping-pong --role tx    # two-dongle ping-pong demo
just test-commands          # exercise all DongLoRa commands
just bridge --mode server   # LoRa bridge over TCP
```

## Depends On

- [`donglora`](https://github.com/donglora/client-py) — the Python client library
