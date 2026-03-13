# Scale Package

Python package for reading HX711 load cell measurements with averaging and outlier filtering.

## Installation

No installation needed - just import from the parent directory:

```python
from scale import Scale
```

## Quick Start

```python
from scale import Scale

# Initialize and use with context manager (handles cleanup automatically)
with Scale() as scale:
    # Tare (zero) the scale
    scale.tare()

    # Get a weight measurement
    weight, num_readings = scale.get_weight()
    print(f"Weight: {weight:.1f} g")
```

## API Reference

### `Scale(dout_pin=5, sck_pin=6, reference_unit=114, calibration_factor=-0.1602059)`

Initialize the scale with HX711 sensor.

**Parameters:**
- `dout_pin`: GPIO pin for DOUT (default: 5)
- `sck_pin`: GPIO pin for SCK (default: 6)
- `reference_unit`: Base reference unit for HX711 (default: 114)
- `calibration_factor`: Final calibration multiplier (default: -0.1602059)

### `tare()`

Reset the scale offset (zero the scale). Returns the new offset value.

### `get_weight(duration=0.5, outlier_stdev=2)`

Get averaged weight measurement with outlier filtering.

**Parameters:**
- `duration`: Time window in seconds to collect readings (default: 0.5)
- `outlier_stdev`: Number of standard deviations for outlier filtering (default: 2)

**Returns:**
- `tuple`: (average_weight_in_grams, number_of_readings)

### `cleanup()`

Cleanup GPIO resources. Called automatically when using context manager.

## Examples

See [example_scale_usage.py](../example_scale_usage.py) for detailed usage examples.

### Continuous Monitoring

```python
from scale import Scale

with Scale() as scale:
    scale.tare()

    while True:
        weight, n = scale.get_weight()
        print(f"Weight: {weight:.1f} g (from {n} readings)")
```

### Custom Calibration

```python
# Use your own calibration factor
scale = Scale(calibration_factor=-0.1602059)
```

### Faster/Slower Readings

```python
# Take measurements over 1 second for more stability
weight, n = scale.get_weight(duration=1.0)

# Take measurements over 0.2 seconds for faster response
weight, n = scale.get_weight(duration=0.2)
```
