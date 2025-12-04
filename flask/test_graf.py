import base64
from io import BytesIO
from matplotlib.figure import Figure
import numpy as np
from scipy.signal import butter, filtfilt
from matplotlib.ticker import MultipleLocator

def generate_ecg_graph():
    adc = []
    tid = []
    lom = []
    lop = []

    with open("recv_data.txt", "r") as f:
        for line in f:       
            clean = line.strip()
            data = clean.split(",")
            tid.append(int(data[0]))
            adc.append(int(data[1]))
            lom.append(int(data[2]))
            lop.append(int(data[3]))
    tid = np.array(tid)
    tid_ms = np.array(tid)
    adc =  np.array(adc)
    lom =  np.array(lom)
    lop =  np.array(lop)


    mask = (lom == 0) & (lop == 0)
    tid  = tid[mask]
    adc = adc[mask]

    tid = (tid - tid[0]) / 1000.0

    adc_mean = adc.mean()
    adc_detr = adc - adc_mean

    dt = np.diff(tid_ms) / 1000.0 

    dt_med = np.median(dt)
    fs = 1.0 / dt_med 
    
    # Design a 4th order Butterworth bandpass
    lowcut = 0.5   # Hz
    highcut = 40.0 # Hz
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    b, a = butter(N=4, Wn=[low, high], btype='bandpass')

    mask_time = (tid <= 10) & (tid >= 0)
    t_zoom = tid[mask_time]
    adc_zoom = adc_detr[mask_time]

    ecg_bp = filtfilt(b, a, adc_zoom)


    fig = Figure(figsize=(10, 5))
    ax = fig.add_subplot() 

    ax.plot(t_zoom, ecg_bp)  

    ax.xaxis.set_major_locator(MultipleLocator(1))

    ax.grid(True)

   

    ax.set_ylabel("ADC")
    ax.set_xlabel("Time (s)") 
    ax.set_title("ECG Data")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data



