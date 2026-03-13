#!/usr/bin/env python3
"""Test script for continuous weight monitoring using the scale package."""

from scale import Scale
import sys

# Configuration
DOUT_PIN = 6
SCK_PIN = 5
REFERENCE_UNIT = 114
CALIBRATION_FACTOR = -0.1602059

# Initialize scale
print("[INFO] Initializing scale...")
scale = Scale(
    dout_pin=DOUT_PIN,
    sck_pin=SCK_PIN,
    reference_unit=REFERENCE_UNIT,
    calibration_factor=CALIBRATION_FACTOR
)

try:
    # Reset (tare) the scale
    print("[INFO] Resetting scale (taring)...")
    offset = scale.tare()
    print(f"[INFO] Offset set to: {offset}")
    print("[INFO] Place weight on scale. Press Ctrl+C to exit.\n")

    # Continuously read and print weight
    while True:
        weight, num_readings = scale.get_weight(duration=0.5)
        print(f"Weight: {weight:.1f} g (n={num_readings})")

except KeyboardInterrupt:
    print("\n[INFO] Exiting and cleaning up GPIO...")
finally:
    scale.cleanup()
    sys.exit()
