set shell := ["bash", "-c"]

_proj := source_directory()
_uv := "uv run --project " + _proj

[private]
_ensure_tools:
    @mise trust --yes . 2>/dev/null; mise install --quiet

# Run all checks (fmt, lint)
check: fmt-check lint

# Format code
fmt: _ensure_tools
    @uv run ruff format .

# Check formatting without changing files
fmt-check: _ensure_tools
    @uv run ruff format --check .

# Lint
lint: _ensure_tools
    @uv run ruff check .

# Receive LoRa packets (Ctrl-C to stop)
rx *args: _ensure_tools
    @{{_uv}} {{source_directory()}}/simple_rx.py {{args}}

# Transmit a single packet
tx *args: _ensure_tools
    @{{_uv}} {{source_directory()}}/simple_tx.py {{args}}

# Two-dongle ping-pong demo (--role tx|rx)
ping-pong *args: _ensure_tools
    @{{_uv}} {{source_directory()}}/ping_pong.py {{args}}

# Probe the connected DongLoRa: dump GET_INFO and exercise one TX + RX
explore *args: _ensure_tools
    @{{_uv}} {{source_directory()}}/explore.py {{args}}

# Two-way LoRa bridge over TCP
bridge *args: _ensure_tools
    @{{_uv}} {{source_directory()}}/lora_bridge.py {{args}}
