from time import sleep, ticks_ms
from machine import Pin, ADC

ecg = ADC(Pin(34, Pin.IN))
ecg.atten(ADC.ATTN_11DB)

lo_min = Pin(25, Pin.IN)
lo_plus = Pin(26, Pin.IN)

sdn = Pin(23, Pin.OUT)

sdn.value(1)
print(sdn.value())

print("\nECG Measurement program successfully loaded.")
print("Measurement beginning in 5 seconds...")
sleep(1)
for i in range(4, 0, -1):
    print(f"{i} seconds...")
    sleep(1)

start = ticks_ms()

with open("ecg.txt", "w") as f:
    while ticks_ms() - start < 10000:
        t = ticks_ms()
        inp = ecg.read()
        lop = lo_plus.value()
        lom = lo_min.value()
        f.write(f"{t},{inp},{lom},{lop}\n")
                
        #print(f"ADC: {inp} | LO-: {lom} | LO+: {lop} | SDN: {sdn.value()}")
        sleep(0.003)
