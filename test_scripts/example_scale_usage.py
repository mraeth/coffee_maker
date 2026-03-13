#!/usr/bin/env python3
"""Example usage of the scale package."""

from scale import Scale
import time

# Example 1: Basic usage with context manager (recommended)
print("Example 1: Using context manager")
with Scale() as scale:
    # Tare the scale
    print(f"Taring scale... Offset: {scale.tare()}")
    print("Place weight on scale.\n")

    # Take 5 measurements
    for i in range(5):
        weight, num_readings = scale.get_weight()
        print(f"Measurement {i+1}: {weight:.1f} g (based on {num_readings} readings)")
        time.sleep(1)

print("\n" + "="*50 + "\n")

# Example 2: Manual cleanup
print("Example 2: Manual initialization and cleanup")
scale = Scale(dout_pin=5, sck_pin=6)

try:
    scale.tare()
    print("Taking continuous measurements (Ctrl+C to stop)...\n")

    while True:
        weight, n = scale.get_weight(duration=0.5)
        print(f"Weight: {weight:.1f} g (n={n})")

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    scale.cleanup()

print("\n" + "="*50 + "\n")

# Example 3: Quick single measurement
print("Example 3: Quick single measurement")
with Scale() as scale:
    scale.tare()
    weight, _ = scale.get_weight()
    print(f"Weight: {weight:.1f} g")
