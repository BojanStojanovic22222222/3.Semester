import network
import time

WIFI_SSID = "7D"
WIFI_PASS = "Gruppe7d"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)

    timeout = 15
    while not wlan.isconnected() and timeout > 0:
        print("Forbinder til Wi-Fi...", timeout)
        time.sleep(1)
        timeout -= 1

    if wlan.isconnected():
        print("Wi-Fi forbundet:", wlan.ifconfig())
    else:
        print("Kunne ikke forbinde til Wi-Fi")

connect_wifi()

print("boot.py færdig – starter main.py...")