# Changelog

## 1.0.0 — 2026-04-22

Initial public release of the example scripts, aligned to the 1.0
DongLoRa stack (`donglora` 1.0 / `donglora-mux` 1.0 /
`donglora-protocol` 1.0).

### Added

- `_common.py`: the shared MeshCore US preset (910.525 MHz /
  BW 62.5 / SF 7 / CR 4/5 / sync 0x1424 / 20 dBm) plus small helpers,
  imported by every script so the scripts themselves stay short.
- `explore.py`: print device capabilities then run one TX + RX
  roundtrip. Useful as a first-run hardware sanity check.
- `simple_rx.py`, `simple_tx.py`: minimal async receive / transmit
  loops built against `donglora.Dongle`.
- `ping_pong.py`: two-dongle ping-pong demo over LoRa.
- `lora_bridge.py`: two-way LoRa bridge over TCP.

### Removed

- `all_commands.py`: indexed the old v0.1 command enum that no longer
  exists after the Protocol v2 split.

### Notes

- Not published to PyPI. Run via `just <recipe>` or
  `uv run --project . <script>` from the examples directory. Local
  dev uses the `[tool.uv.sources]` editable path to `../client-py`;
  the declared registry dep is `donglora>=1.0.0,<2.0.0`.
