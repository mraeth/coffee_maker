# Bluetooth Serial Communication

## Hardware

| Component | Detail |
|-----------|--------|
| Module | HC-06 |
| MAC | `98:D3:31:40:19:91` |
| PIN | `1234` |
| RFCOMM channel | `1` |
| Arduino RX | D5 |
| Arduino TX | D4 |
| Baud rate | 9600 |

## Arduino Pins

| Pin | Role |
|-----|------|
| D2 | SSD (heater element relay signal) |
| D3 | Pump relay |
| D4 | HC-06 TX → Arduino RX via SoftwareSerial |
| D5 | HC-06 RX ← Arduino TX via SoftwareSerial |

> D5 is the SoftwareSerial RX pin — **do not use it for anything else** (it was previously the pump relay, causing conflicts).

## Protocol

Commands are always **2 bytes**: a letter identifying the actuator followed by `'1'` (on) or `'0'` (off).

| Command | Effect |
|---------|--------|
| `H1` | Heater ON (D2 HIGH) |
| `H0` | Heater OFF (D2 LOW) |
| `P1` | Pump ON (D3 HIGH) |
| `P0` | Pump OFF (D3 LOW) |

## One-time Setup

### 1. Pair the HC-06

```bash
bluetoothctl
  power on
  agent on
  scan on          # wait for 98:D3:31:40:19:91 to appear
  scan off
  pair 98:D3:31:40:19:91   # enter PIN: 1234
  trust 98:D3:31:40:19:91
  quit
```

### 2. RFCOMM permissions (avoid sudo on every connect)

```bash
sudo usermod -aG bluetooth $USER   # then log out/in
# or grant cap_net_admin to the rfcomm binary:
sudo setcap 'cap_net_admin+ep' $(which rfcomm)
```

## Python Usage

`bluetooth_serial.py` wraps the kernel RFCOMM driver (`/dev/rfcomm0`) instead of raw Bluetooth sockets, matching the reliability of bash-level `rfcomm connect`.

```python
from bluetooth_serial import BluetoothSerial

# context manager — recommended
with BluetoothSerial() as bt:
    bt.write("P1")   # pump on
    bt.write("P0")   # pump off

# manual
bt = BluetoothSerial()
bt.write("H1")   # auto-connects on first write
bt.close()
```

### How it works

1. `connect()` calls `rfcomm bind 0 <MAC> 1` to register `/dev/rfcomm0`
2. Opening `/dev/rfcomm0` triggers the actual BT connection
3. All I/O goes through the kernel RFCOMM driver (same path as bash)
4. `close()` releases the device with `rfcomm release 0`
