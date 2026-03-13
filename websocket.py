import time
import threading
import asyncio
import json
import websockets

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

from scale import Scale


# ---- Scale initialization ----
DOUT_PIN = 6
SCK_PIN = 5
REFERENCE_UNIT = 114
CALIBRATION_FACTOR = -0.1602059

scale = Scale(
    dout_pin=DOUT_PIN,
    sck_pin=SCK_PIN,
    reference_unit=REFERENCE_UNIT,
    calibration_factor=CALIBRATION_FACTOR
)

print("[INFO] Taring scale...")
scale.tare()
print("[INFO] Scale ready.")

latest_weight = 0.0
latest_temperature = 0.0

_weight_lock = threading.Lock()
_hx_lock = threading.Lock()

MAX_WEIGHT_JUMP_G = 10.0


def _scale_reader_thread():
    global latest_weight, latest_temperature

    while True:
        try:
            with _hx_lock:
                weight, temperature = scale.get_weight(duration=0.3)

            with _weight_lock:
                prev = latest_weight

            if abs(weight - prev) > MAX_WEIGHT_JUMP_G:
                with _hx_lock:
                    weight, temperature = scale.get_weight(duration=0.3)

            with _weight_lock:
                latest_weight = weight
                latest_temperature = temperature

        except Exception as e:
            print(f"[WARN] Scale read error: {e}")
            time.sleep(0.1)


threading.Thread(target=_scale_reader_thread, daemon=True).start()


# ---- WebSocket server ----

async def scale_stream(websocket):
    global latest_weight

    print("[INFO] Client connected")

    try:
        while True:
            # Handle any incoming commands without blocking
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=0.05)
                if msg.strip() == "tare":
                    print("[INFO] Tare requested")
                    with _hx_lock:
                        scale.tare()
                    with _weight_lock:
                        latest_weight = 0.0
            except asyncio.TimeoutError:
                pass

            with _weight_lock:
                weight = latest_weight
                temperature = latest_temperature

            data = {
                "weight_g": round(weight, 2),
                "temperature_c": round(temperature, 2),
                "timestamp": time.time()
            }

            await websocket.send(json.dumps(data))

            await asyncio.sleep(0.1)  # 10 Hz updates

    except websockets.ConnectionClosed:
        print("[INFO] Client disconnected")


async def main():
    async with websockets.serve(scale_stream, "0.0.0.0", 8061):
        print("[INFO] WebSocket server running on port 8061")
        await asyncio.Future()  # run forever


asyncio.run(main())