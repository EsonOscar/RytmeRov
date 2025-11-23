from time import sleep
from matplotlib import pyplot as plt
import numpy as np

data = []
index = 0
t = []
adc = []
lom = []
lop = []

with open("ecg.txt", "r") as f:
    for line in f:
        clean = line.strip()
        """
        data = clean.split(",")
        for i in range(len(data)):
            data[i] = int(data[i])
        #print(data, f"LOM: {data[2]}, LOP: {data[3]}")
        if data[2] == 0 and data[3] == 0:
            #print("TEST")
            x.append(data[0])
            y.append(data[1])
        #print(f"Time: {data[0]} | ADC: {data[1]}")
        """
        data = clean.split(",")
        ti, ai, lomi, lopi = map(int, data)
        t.append(ti)
        adc.append(ai)
        lom.append(lomi)
        lop.append(lopi)
        
t = np.array(t)
adc = np.array(adc)
lom = np.array(lom)
lop = np.array(lop)
        
mask = (lom == 0) & (lop == 0)
t = t[mask]
adc = adc[mask]

t = (t - t[0]) / 1000.0

adc_mean = adc.mean()
adc_detr = adc - adc_mean
        
#print(x, y)

mask_time = (t <= 10) & (t >= 0)
t_zoom = t[mask_time]
adc_zoom = adc_detr[mask_time]

fig, ax = plt.subplots()

ax.plot(t_zoom, adc_zoom)
plt.ylabel("ADC")
plt.xlabel("Time (s)")

#ax.set_ylim(0, 4096)
#ax.set_xlim(t[0], t[-1])
plt.grid(True)
plt.show()

exit()