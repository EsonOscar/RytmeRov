import numpy as np
import math

with open("/home/3semprojekt/RytmeRov/flask/clean_recv_data.csv", "r") as f:
    data = f.read()
    
    data = data.strip().split("\n")

    t = []
    adc = []
    
    for i in range(len(data)):
        split = data[i].split(",")
        t.append(float(split[0]))
        adc.append(float(split[1]))

print(len(t) == len(adc))

high = 0
low = 0
for elem in adc:
    if elem > high:
        high = elem
    if elem < low:
        low = elem

print(high, low)

cut = 0.8 * high
print(cut)
rf = 0.25
prev_beat = 0
beats = 0

for i in range (len(adc)):
    if t[i] < 2:
        pass
    else:
        if adc[i] >= cut:
            if t[i] > (prev_beat + rf):
                beats += 1
                prev_beat = t[i]
            else:
                pass
        else:
            pass

print(beats)
        