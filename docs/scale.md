# Scale Library

## Hardware

| Component | Detail |
|-----------|--------|
| ADC | HX711 |
| DOUT pin | GPIO 6 (BCM) |
| SCK pin | GPIO 5 (BCM) |
| Reference unit | 114 |
| Calibration factor | −0.1602059 |

The HX711 driver is loaded from `deps/hx711py/` and uses MSB-first format for both data and clock.

## Setup

No installation required — import directly:

```python
from scale import Scale
```

Depends on `RPi.GPIO` and the bundled `hx711py` library in `deps/`.

## API

### `Scale(dout_pin, sck_pin, reference_unit, calibration_factor)`

| Parameter | Default | Description |
|-----------|---------|-------------|
| `dout_pin` | `5` | GPIO DOUT pin (BCM) |
| `sck_pin` | `6` | GPIO SCK pin (BCM) |
| `reference_unit` | `114` | HX711 reference unit |
| `calibration_factor` | `−0.1602059` | Multiplier applied to raw weight |

### `tare()`

Zeros the scale by auto-setting the HX711 offset. Returns the new offset value.

### `get_weight(duration=0.5, outlier_stdev=2)`

Collects raw readings for `duration` seconds, removes statistical outliers, and returns the mean.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `duration` | `0.5` | Sampling window in seconds |
| `outlier_stdev` | `2` | Readings beyond N standard deviations are discarded |

Returns `(weight_g: float, num_readings: int)`.

Outlier filtering requires at least 3 readings; fewer readings return a plain mean. If all readings are filtered out the unfiltered mean is used as fallback.

### `cleanup()`

Releases GPIO resources. Called automatically by the context manager.

## Usage

```python
from scale import Scale

with Scale(dout_pin=6, sck_pin=5) as scale:
    scale.tare()
    weight, n = scale.get_weight(duration=0.3)
    print(f"{weight:.2f} g  ({n} samples)")
```

### Tuning duration

| `duration` | Samples (approx) | Use case |
|-----------|-----------------|----------|
| `0.2` | ~15 | Fast UI updates |
| `0.3` | ~22 | Default in websocket server |
| `0.5` | ~35 | More stable readings |
| `1.0` | ~70 | Maximum stability |
