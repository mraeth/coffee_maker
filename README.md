# Pour-Over Coffee Maker

A smart scale and automated pour-over coffee brewing system running on Raspberry Pi.

## Overview

1. **Smart Scale** — Real-time weight and temperature monitoring via a web dashboard and WebSocket stream
2. **Bluetooth Control** — Heater and pump relay control via HC-06 Bluetooth module connected to an Arduino
3. **Automated Pouring** (planned) — Recipe-driven water pouring sequences

## Hardware

- Raspberry Pi
- HX711 load cell ADC (DOUT: GPIO 6, SCK: GPIO 5)
- Temperature probe (read via HX711)
- HC-06 Bluetooth module (MAC: `98:D3:31:40:19:91`, channel 1)
- Arduino controlling heater relay (D2) and pump relay (D3)

## Project Structure

```
coffee_maker/
├── websocket.py            # WebSocket server — streams scale data at 10 Hz (port 8061)
├── bluetooth_serial.py     # HC-06 Bluetooth serial wrapper (heater/pump control)
├── scale/                  # Scale library (HX711 + outlier filtering)
│   ├── __init__.py
│   └── reader.py
├── test_scripts/
│   ├── test_webserver.py   # Dash web dashboard (port 8060)
│   ├── example_scale_usage.py
│   ├── test_cell_io.py
│   └── plot_data.py
├── deps/
│   └── hx711py/            # Vendored HX711 driver
├── docs/
│   ├── scale.md
│   ├── websocket.md
│   └── bluetooth.md
├── data/                   # Saved brewing session CSVs (gitignored)
├── assets/
│   └── cyborg.min.css      # Bootstrap theme for dashboard
└── requirements.txt
```

## Installation

```bash
git clone https://github.com/mraeth/coffee_maker.git
cd coffee_maker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`RPi.GPIO` must be installed separately on the Raspberry Pi:

```bash
pip install RPi.GPIO
```

## Usage

### WebSocket scale stream

```bash
python websocket.py
```

Streams JSON at 10 Hz on port 8061:

```json
{"weight_g": 123.45, "temperature_c": 24.10, "timestamp": 1741872000.123}
```

Send `"tare"` from the client to zero the scale.

### Web dashboard

```bash
python test_scripts/test_webserver.py
# or for production:
gunicorn test_scripts.test_webserver:server -b 0.0.0.0:8060
```

Access at `http://<raspberry-pi-ip>:8060`.

### Bluetooth control

```python
from bluetooth_serial import BluetoothSerial

with BluetoothSerial() as bt:
    bt.write("H1")   # heater on
    bt.write("P1")   # pump on
    bt.write("P0")   # pump off
    bt.write("H0")   # heater off
```

See [docs/bluetooth.md](docs/bluetooth.md) for the full command reference.

## Scale Configuration

Default calibration values in `websocket.py` and `test_scripts/test_webserver.py`:

```python
DOUT_PIN = 6
SCK_PIN  = 5
REFERENCE_UNIT     = 114
CALIBRATION_FACTOR = -0.1602059
```

See [docs/scale.md](docs/scale.md) for the full API reference.

## Roadmap

- [x] Real-time scale monitoring (web dashboard + WebSocket)
- [x] Bluetooth relay control (heater + pump)
- [ ] Automated pouring sequences driven by recipes
- [ ] Recipe management UI
- [ ] Brewing profiles and presets
