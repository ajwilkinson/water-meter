#!/usr/bin/env python3
"""
Water meter pulse logger for Raspberry Pi.

Watches a reed switch / pulse sensor on GPIO 17 (physical pin 11), wired
between the pin and ground. Each time the pin is pulled low, it writes a
point to InfluxDB (1.x HTTP /write API).

Dependencies (preinstalled on Raspberry Pi OS; otherwise):
    sudo apt install python3-gpiozero python3-lgpio
"""

import logging
import os
import queue
import signal
import threading
import urllib.error
import urllib.request

from gpiozero import Button

GPIO_PIN = int(os.environ.get("WATER_METER_GPIO", "17"))  # BCM numbering
DEBOUNCE_SECONDS = 0.05      # 50 ms, same as the original
URL = "http://workshop.local:8086/write?db=water"
PAYLOAD = b"water,location=Home used=10"
HTTP_TIMEOUT = 10            # seconds

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("water-meter")

# Pulses go into a queue so a slow or unreachable InfluxDB server never
# blocks the GPIO callback and causes missed pulses.
pulses: "queue.Queue[None]" = queue.Queue()


def on_pulse() -> None:
    pulses.put(None)


def post_point() -> None:
    req = urllib.request.Request(
        URL,
        data=PAYLOAD,
        method="POST",
        headers={"Content-Type": "text/plain; charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        if resp.status not in (200, 204):
            log.error("InfluxDB returned HTTP %s", resp.status)


def sender() -> None:
    while True:
        pulses.get()
        try:
            post_point()
        except (urllib.error.URLError, OSError) as exc:
            log.error("Failed to write to InfluxDB: %s", exc)
        finally:
            pulses.task_done()


def main() -> None:
    # pull_up=True: the pin idles high and a pulse pulls it to ground,
    # so "pressed" is the transition to 0 (what the JS checked for).
    sensor = Button(GPIO_PIN, pull_up=True, bounce_time=DEBOUNCE_SECONDS)
    sensor.when_pressed = on_pulse

    threading.Thread(target=sender, daemon=True).start()

    log.info("water-meter ready")
    signal.pause()  # sleep until killed; callbacks run in the background


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass