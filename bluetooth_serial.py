"""
Minimal Bluetooth serial library for HC-06 communication.

Uses rfcomm bind + /dev/rfcomm<n> (kernel RFCOMM driver) — the same path
as bash / rfcomm connect, which is far more reliable than raw AF_BLUETOOTH
sockets via BlueZ's user-space API.

HC-06 MAC: 98:D3:31:40:19:91
PIN:       1234
RFCOMM channel: 1 (HC-06 default)

Requires: rfcomm binary (bluez package) and permission to run it.
If rfcomm bind needs sudo, add a udev rule or run once with sudo.
"""

import io
import subprocess
import time

HC06_MAC = "98:D3:31:40:19:91"
HC06_CHANNEL = 1


class BluetoothSerial:
    def __init__(
        self,
        mac: str = HC06_MAC,
        channel: int = HC06_CHANNEL,
        rfcomm_dev: int = 0,
    ):
        self.mac = mac
        self.channel = channel
        self.dev = f"/dev/rfcomm{rfcomm_dev}"
        self._rfcomm_dev = rfcomm_dev
        self._file: io.RawIOBase | None = None

    def connect(self) -> None:
        self.close()
        subprocess.run(
            ["rfcomm", "bind", str(self._rfcomm_dev), self.mac, str(self.channel)],
            check=True,
        )
        # Opening the device triggers the actual BT connection
        self._file = open(self.dev, "r+b", buffering=0)

    def write(self, data: bytes | str) -> None:
        if self._file is None:
            self.connect()
        if isinstance(data, str):
            data = data.encode()
        self._file.write(data)

    def read(self, n: int = 256, timeout: float = 1.0) -> bytes:
        import select
        ready, _, _ = select.select([self._file], [], [], timeout)
        if not ready:
            return b""
        return self._file.read(n) or b""

    def readline(self, timeout: float = 2.0) -> bytes:
        buf = bytearray()
        deadline = time.monotonic() + timeout
        import select
        while time.monotonic() < deadline:
            remaining = deadline - time.monotonic()
            ready, _, _ = select.select([self._file], [], [], remaining)
            if not ready:
                break
            ch = self._file.read(1)
            if not ch:
                break
            buf += ch
            if ch == b"\n":
                break
        return bytes(buf)

    def close(self) -> None:
        if self._file:
            self._file.close()
            self._file = None
        subprocess.run(
            ["rfcomm", "release", str(self._rfcomm_dev)],
            capture_output=True,
        )

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_):
        self.close()
