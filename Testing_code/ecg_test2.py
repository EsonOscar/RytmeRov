from time import sleep, ticks_ms
from machine import Pin, ADC, SoftI2C
from ads1x15 import ADS1015

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))

ads = ADS1015(i2c)

#ecg = ADC(Pin(34, Pin.IN))
#ecg.atten(ADC.ATTN_11DB)

lo_min = Pin(25, Pin.IN)
lo_plus = Pin(26, Pin.IN)

sdn = Pin(23, Pin.OUT)

print("Restarting ECG sensor...")
sdn.value(0)
print(sdn.value())
sleep(2)
sdn.value(1)
print(sdn.value())
if sdn.value() == 1:
    print("ECG sensor successfully restarted!\n")
else:
    print("Error restarting sensor, quitting program...")
    exit()


print("\nECG Measurement program successfully loaded.")
print("Measurement beginning in 5 seconds...")
sleep(1)
for i in range(4, 0, -1):
    print(f"{i} seconds...")
    sleep(1)

start = ticks_ms()

while True:#ticks_ms() - start < 20000:
    t = ticks_ms()
    inp = ads.read(0)
    lop = lo_plus.value()
    lom = lo_min.value()
    #if lom == 0 and lop == 0:
    print(f"LO-: {lom} | LO+: {lop} | ADC: {inp} | SDN: {sdn.value()}")
    sleep(0.1)
