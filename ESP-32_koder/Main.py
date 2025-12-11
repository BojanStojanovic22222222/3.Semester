from machine import I2C, Pin, PWM
import time
import dht
import urequests
from max30100 import MAX30100
import neopixel


SERVER_URL = "http://192.168.0.11:5000/api/data"


dht_sensor = dht.DHT11(Pin(4))

def read_temperature():
    try:
        dht_sensor.measure()
        return dht_sensor.temperature()
    except:
        return None



i2c = I2C(0, scl=Pin(22), sda=Pin(21))
sensor = MAX30100(i2c)

print("Pulsoximeter klient startet")



NUM_PIXELS = 12
np = neopixel.NeoPixel(Pin(15), NUM_PIXELS)

def ring_color(r, g, b):
    for i in range(NUM_PIXELS):
        np[i] = (r, g, b)
    np.write()



servo = PWM(Pin(18), freq=50)

def angle_to_duty(angle):
    min_duty = 26
    max_duty = 128
    return int(min_duty + (max_duty - min_duty) * (angle / 180))

def servo_set_angle(angle):
    servo.duty(angle_to_duty(angle))

def servo_alarm():
    servo_set_angle(40)
    time.sleep_ms(120)
    servo_set_angle(140)
    time.sleep_ms(120)
    servo_set_angle(90)



VIB_A = Pin(23, Pin.OUT)
VIB_B = Pin(19, Pin.OUT)

def vib_on():
    VIB_A.value(1)
    VIB_B.value(0)

def vib_off():
    VIB_A.value(0)
    VIB_B.value(0)

def vib_pulse(ms=120):
    vib_on()
    time.sleep_ms(ms)
    vib_off()



def sanitize_values(bpm, spo2, temp):

  
    if bpm is None or bpm <= 30 or bpm > 250:
        bpm = 70

   
    if spo2 is None or spo2 < 80 or spo2 > 100:
        spo2 = 97

    
    if temp is None or temp < 20 or temp > 45:
        temp = 36.5

    return int(bpm), int(spo2), float(temp)


def send_data(bpm, spo2, temp):

    bpm, spo2, temp = sanitize_values(bpm, spo2, temp)

    payload = {
        "patient_id": 1,
        "bpm": bpm,
        "spo2": spo2,
        "temperature": temp,
        "timestamp": time.time()
    }

    try:
        print("Sender til server:", payload)
        r = urequests.post(SERVER_URL, json=payload)
        print("Status:", r.status_code)
        r.close()
    except Exception as e:
        print("Fejl ved POST:", e)


def handle_temperature(temp):
    if temp is None:
        ring_color(40, 40, 0)
        return

    if temp < 25:
        ring_color(0, 0, 80)
    elif 25 <= temp <= 32:
        ring_color(0, 80, 0)
    else:
        ring_color(80, 0, 0)
        vib_pulse()
        servo_alarm()


def smooth(values, window=8):
    if len(values) < window:
        return sum(values) / len(values)
    return sum(values[-window:]) / window


ir_buffer = []
red_buffer = []

last_peak_time = time.ticks_ms()
bpm = 0
spo2 = 0

print("Måling startet")

while True:
    try:
        ir, red = sensor.read_raw()

        if ir < 8000:
            print("Sæt finger på sensoren")
            ring_color(0, 0, 40)
            time.sleep(0.3)
            continue

        ir_buffer.append(ir)
        red_buffer.append(red)

        if len(ir_buffer) > 120:
            ir_buffer.pop(0)
            red_buffer.pop(0)

        ir_s = smooth(ir_buffer, 10)
        threshold = ir_s * 1.008

        if ir > threshold:
            now = time.ticks_ms()
            interval = time.ticks_diff(now, last_peak_time)

            if interval > 400:
                bpm_candidate = 60000 / interval

                if 50 < bpm_candidate < 150:
                    bpm = int(bpm_candidate)
                else:
                    bpm = 70

                ir_ac = max(ir_buffer) - min(ir_buffer)
                red_ac = max(red_buffer) - min(red_buffer)
                ir_dc = sum(ir_buffer) / len(ir_buffer)
                red_dc = sum(red_buffer) / len(red_buffer)

                if ir_dc > 0 and red_dc > 0:
                    R = (red_ac/red_dc) / (ir_ac/ir_dc)
                    spo2_calc = int(110 - 25 * R)

                    if 80 <= spo2_calc <= 100:
                        spo2 = spo2_calc
                    else:
                        spo2 = 97

                temp_raw = read_temperature()
                if temp_raw is None or temp_raw < 20 or temp_raw > 45:
                    temp = 36.5
                else:
                    temp = temp_raw

                print("BPM:", bpm, "SpO2:", spo2, "Temp:", temp)

                handle_temperature(temp)
                send_data(bpm, spo2, temp)

                last_peak_time = now

        time.sleep(0.02)

    except Exception as e:
        print("Fejl:", e)
        ring_color(80, 0, 0)
        time.sleep(0.5)