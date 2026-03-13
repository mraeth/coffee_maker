# WebSocket Scale Server

## Overview

`websocket.py` runs a WebSocket server on the Raspberry Pi that streams live scale (weight + temperature) readings at 10 Hz and accepts a `tare` command from any connected client.

## Hardware

| Component | Detail |
|-----------|--------|
| Load cell ADC | HX711 |
| DOUT pin | GPIO 6 (BCM) |
| SCK pin | GPIO 5 (BCM) |
| Reference unit | 114 |
| Calibration factor | −0.1602059 |

## Server

| Parameter | Value |
|-----------|-------|
| Port | `8061` |
| Bind address | `0.0.0.0` (all interfaces) |
| Update rate | 10 Hz |

## Message Format

The server pushes a JSON object to every connected client at 10 Hz:

```json
{
  "weight_g": 123.45,
  "temperature_c": 24.10,
  "timestamp": 1741872000.123
}
```

## Commands (client → server)

| Message | Effect |
|---------|--------|
| `tare` | Tares the scale and resets `weight_g` to `0.0` |

## Setup & Running

### Dependencies

```bash
pip install websockets RPi.GPIO
```

### Start the server

```bash
python websocket.py
```

The scale is tared once on startup. The server then runs indefinitely.

### Connect (example)

```python
import asyncio, websockets, json

async def main():
    async with websockets.connect("ws://<pi-ip>:8061") as ws:
        while True:
            data = json.loads(await ws.recv())
            print(data["weight_g"], "g")

asyncio.run(main())
```

Send a tare:

```python
await ws.send("tare")
```

## Architecture

A background daemon thread reads the HX711 continuously via `scale.get_weight(duration=0.3)`. If a single reading jumps more than **10 g** from the previous value it is re-sampled once to reject noise. The WebSocket handler reads the latest cached values under a lock — the sensor is never accessed directly from the async event loop.
