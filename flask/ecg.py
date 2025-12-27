import numpy as np
from io import BytesIO
from cryptography.fernet import Fernet
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator
from scipy.signal import butter, filtfilt
import statistics as stats
import base64
import os
from sys import exit

db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_port = os.environ.get("DB_PORT")
db_name = os.environ.get("DB_NAME")

key = os.environ.get("ENC_KEY")
fer = Fernet(key.encode())

pepper = os.environ.get("CPR_PEPPER")

# Take a raw ECG measurement and make it oh so beautiful
# REWRITE TO TAKE A DECRYPTED SET OF LISTS INSTEAD OF FILE
# Done, good job little Oscar
def filter_raw_ecg(t, adc, lom, lop, start_time=0, stop_time=22):
    """
    Takes a raw unfiltered ECG measurement containing times in ms, ADC values, LOP and LOM (electrode contact)
    and filters it, to produce two clean output lists, t and adc.
    """
    """
    adc = []
    t = []
    lom = []
    lop = []

    count = 0
    
    
    # REWRITE TO TAKE A DECRYPTED SET OF LISTS INSTEAD OF FILE
    with open(filepath, "r") as f:
        for line in f:
            #print(count)
            if count == 0:
                pass
            else:       
                clean = line.strip()
                data = clean.split(",")
                tid.append(int(data[0]))
                adc.append(int(data[1]))
                lom.append(int(data[2]))
                lop.append(int(data[3]))
            count = count + 1
    """
    #print(tid)
    
    
    
    t = np.array(t)
    t_ms = np.array(t)
    adc =  np.array(adc)
    lom =  np.array(lom)
    lop =  np.array(lop)


    mask = (lom == 0) & (lop == 0)
    t  = t[mask]
    adc = adc[mask]
    
    # Remove the first 2 seconds of the measurement
    # Stupid sensor is finicky right after startup
    cut = t[0] + 2000
    t = t - cut
    time_mask = (t > 0)
    #print(t)
    t = t[time_mask]
    adc = adc[time_mask]
    
    #print(t)

    # If all data rows are filtered out due to bad electrode contact, exit function
    if len(t) == 0 or len(adc) == 0:
        print("No usable data, exiting ECG graph function...")
        return
    
    # Error happened here once, t[0] out of index?
    # Happens when all rows are deleted in filtering
    #print(t)
    try:
        t = (t - t[0]) / 1000.0
    except Exception as e:
        print(f"Error when loading graph data, exiting.")
        print(f"Error: {e}")
        
        exit(1)
    
    #print(f"ADC: {adc}")
    adc_mean = adc.mean()
    #print(f"ADC MEAN: {adc_mean}")
    adc_detr = adc - adc_mean
    #print(f"ADC_DETR: {adc_detr}")

    dt = np.diff(t_ms) / 1000.0 

    dt_med = np.median(dt)
    fs = 1.0 / dt_med 
    
    # Design a 4th order Butterworth bandpass
    lowcut = 0.5   # Hz
    highcut = 40.0 # Hz
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    b, a = butter(N=4, Wn=[low, high], btype='bandpass')

    mask_time = (t <= stop_time) & (t >= start_time)
    t_zoom = t[mask_time]
    adc_zoom = adc_detr[mask_time]

    ecg_bp = filtfilt(b, a, adc_zoom)
    
    return t_zoom, ecg_bp

def generate_graph(t_zoom, ecg_bp):
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

# Try to detect R-peaks in a cleaned up ECG measurement
def detect_r_peaks(t, adc, rf_sec=0.2, thresh_factor=5.0):
    """
    Takes a cleaned up ECG measurement and tries to detect the R peaks of the QRS complex.
    """
    
    if len(adc) < 3:
        return []
    
    baseline = stats.median(adc)
    
    adc_centered = []
    for val in adc:
        adc_centered.append(val - baseline)
    
    max_pos = max(adc_centered)
    print(f"Max positive value: {max_pos}")
    max_neg = min(adc_centered)
    print(f"Max negative value: {max_neg}")
    
    #print(max_pos, max_neg)
    
    adc_final = []
    if abs(max_neg) > abs(max_pos):
        for val in adc_centered:
            adc_final.append(-val)
    else:
        adc_final = adc_centered
    
    abs_vals = []
    for val in adc_final:
        abs_vals.append(abs(val))
        
    noise_level = stats.median(abs_vals)
    print("Noise_level: ", noise_level)
    
    if noise_level == 0:
        noise_level = 0.000001
        
    threshold = thresh_factor * noise_level
    print(f"Threshold: {threshold}")
    
    #print("Threshold: ", threshold)
    
    r_indices = []
    last_peak_time = -1000000000
    
    for i in range(1, len(adc_final) - 1):
        if adc_final[i] > adc_final[i - 1] and adc_final[i] >= adc_final[i + 1]:
            if adc_final[i] >= threshold:
                if t[i] - last_peak_time >= rf_sec:
                    r_indices.append(i)
                    last_peak_time = t[i]
                    
    #print("Number of peaks found: ", len(r_indices))
    #print(r_indices)
    
    return r_indices, noise_level


# Final put together version, with data like HR, intervals etc. pretty cool good job Oscar
def analyze_ecg(t, adc, rf_sec=0.15, thresh_factor=5):
    #t, adc = filter_raw_ecg("recv_data.csv")
    
    if len(t) == 0:
        print("No values in the selected dataset")
        return None

    r_indices, noise_level = detect_r_peaks(t, adc, rf_sec, thresh_factor)
    beats = len(r_indices)
    
    if beats < 2:
        print("Not enough beats in the selected dataset")
        return None
    
    r_times = []
    for val in r_indices:
        r_times.append(t[val])
    
    #print(r_times)
    
    rr = []
    for i in range(beats -1):
        rr.append(r_times[i + 1] - r_times[i])
    
    #print(len(rr))
    #print(rr)
    
    rr_mean = stats.mean(rr)
    #print(rr_mean)
    
    hr_per_interval = []
    for val in rr:
        if val == 0:
            break
        else:
            hr_per_interval.append(60 / val)

    #print(hr_per_interval)
    
    if rr_mean != 0:
        hr_mean = 60 / rr_mean
    else:
        hr_mean = None
    
    if len(rr) > 1:
        rr_std = stats.pstdev(rr)
    else:
        rr_std = None
        
    return {
        "beats": beats,
        "r_peak_times": r_times,
        "rr_intervals": rr,
        "rr_mean": rr_mean,
        "rr_std": rr_std,
        "hr_mean": hr_mean,
        "hr_per_interval": hr_per_interval,
        "noise": noise_level
    }
    
def decrypt_ecg(filename):
    filename = filename + ".csv"
    #print(filename)
    
    with open(f"/home/3semprojekt/RytmeRov/flask/ecg/{filename}", "r") as f:
        enc_ecg = f.read()
    
    decr_ecg = fer.decrypt(enc_ecg.encode()).decode().strip().split("\n")
    
    #print(decr_ecg)
    #print(type(decr_ecg))
    
    t = []
    adc = []
    lom = []
    lop = []
    count = 0
    for line in decr_ecg:
        if count == 0:
            count = 1
        else:
            data = line.split(",")
            #print(data)
            t.append(int(data[0]))
            adc.append(int(data[1]))
            lom.append(int(data[2]))
            lop.append(int(data[3]))

    return t, adc, lom, lop
    
if __name__ == "__main__":
    t, adc = filter_raw_ecg("recv_data.csv")
    print("\nFile has been cleaned up, remaining t and adc indices:")
    print(len(t), len(adc), "\n")
    
    r_peaks = detect_r_peaks(t, adc)
    print("Number of R-peaks found:")
    print(len(r_peaks), "\n")
    
    result = analyze_ecg("recv_data.csv")
    print("Analyzed data:")
    print("Found beats:", result.get("beats"))
    print("Average heartrate:", round(result.get("hr_mean"), 2), "beats per minute")
    print("Average RR interval:", round(result.get("rr_mean"), 2), "seconds")
    print("RR intervals standard deviation:", result.get("rr_std"))
    print("Noise level:", result.get("noise"))
    print("Thank the fucking Lord Oscar Ericson for his genius math skills, amen.")
    
    
    
    
    