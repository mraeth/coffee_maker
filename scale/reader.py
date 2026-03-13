import time
import sys
import os
import statistics
import RPi.GPIO as GPIO

# Add deps directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'deps', 'hx711py'))

from hx711v0_5_1 import HX711


class Scale:
    """HX711 load cell reader with averaging and outlier filtering."""

    def __init__(self, dout_pin=5, sck_pin=6, reference_unit=114, calibration_factor=-0.1602059):
        """
        Initialize the scale.

        Args:
            dout_pin: GPIO pin for DOUT
            sck_pin: GPIO pin for SCK
            reference_unit: Base reference unit for HX711
            calibration_factor: Final calibration multiplier
        """
        self.calibration_factor = calibration_factor

        # Initialize HX711
        self.hx = HX711(dout_pin, sck_pin)
        self.hx.setReadingFormat("MSB", "MSB")
        self.hx.setReferenceUnit(reference_unit)

    def tare(self):
        """Reset the scale offset (tare/zero the scale)."""
        self.hx.autosetOffset()
        return self.hx.getOffset()

    def get_weight(self, duration=0.5, outlier_stdev=2):
        """
        Get averaged weight measurement with outlier filtering.

        Args:
            duration: Time window in seconds to collect readings (default: 0.5)
            outlier_stdev: Number of standard deviations for outlier filtering (default: 2)

        Returns:
            tuple: (average_weight_in_grams, number_of_readings)
        """
        readings = []
        start_time = time.time()

        # Collect readings over the duration
        while time.time() - start_time < duration:
            rawBytes = self.hx.getRawBytes()
            weight = self.hx.rawBytesToWeight(rawBytes) * self.calibration_factor
            readings.append(weight)

        if not readings:
            return 0.0, 0

        # Remove outliers if we have enough readings
        if len(readings) >= 3:
            mean = statistics.mean(readings)
            stdev = statistics.stdev(readings)

            # Keep readings within specified standard deviations
            filtered = [r for r in readings if abs(r - mean) <= outlier_stdev * stdev]

            # Use filtered readings if we have any, otherwise use all
            if filtered:
                avg_weight = statistics.mean(filtered)
            else:
                avg_weight = mean
        else:
            avg_weight = statistics.mean(readings)

        return avg_weight, len(readings)

    def cleanup(self):
        """Cleanup GPIO resources."""
        GPIO.cleanup()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()
