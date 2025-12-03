from time import sleep, ticks_ms
from machine import Pin, ADC, I2C
from ads1x15 import ADS1015

lo_min = Pin(25, Pin.IN)
lo_plus = Pin(26, Pin.IN)

i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
ads = ADS1015(i2c)

sdn = Pin(23, Pin.OUT)

sdn.value(0)
sdn.value(1)
print(sdn.value())

print("\nECG Measurement program successfully loaded.")
print("Measurement beginning in:\n5 seconds...")
sleep(1)
for i in range(4, 0, -1):
    print(f"{i} seconds...")
    sleep(1)



count = 0
inp = 0
res = []
start = ticks_ms()

with open("ecg.txt", "w") as f:
    while ticks_ms() - start < 10000:
        t = ticks_ms()
        inp = ads.read(0)
        #inp += 1
        lop = lo_plus.value()
        lom = lo_min.value()
        f.write(f"{t},{inp},{lom},{lop}\n")
        #res.append(f"{t},{inp},{lom},{lop}")        
                
        #print(f"ADC: {inp} | LO-: {lom} | LO+: {lop} | SDN: {sdn.value()}")
        count += 1
        #sleep(0.004)

print(f"\nMeasurements taken: {count}\nFrequency: {count / 10}")
