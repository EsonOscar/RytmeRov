import numpy as np
from scipy.signal import butter, filtfilt
import statistics as stats
from sys import exit

# Take a raw ECG measurement and make it oh so beautiful
def filter_raw_ecg(filepath, start_time=0, stop_time=10):
    """
    Takes a raw unfiltered ECG measurement containing times in ms, ADC values, LOP and LOM (electrode contact)
    and filters it, to produce a two clean output lists, t and adc.
    """
    
    adc = []
    tid = []
    lom = []
    lop = []

    count = 0
    
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
    
    #print(tid)  
    
    tid = np.array(tid)
    tid_ms = np.array(tid)
    adc =  np.array(adc)
    lom =  np.array(lom)
    lop =  np.array(lop)


    mask = (lom == 0) & (lop == 0)
    tid  = tid[mask]
    adc = adc[mask]

    # If all data rows are filtered out due to bad electrode contact, exit function
    if len(tid) == 0 or len(adc) == 0:
        print("No usable data, exiting ECG graph function...")
        return
    
    # Error happened here once, tid[0] out of index?
    # Happens when all rows are deleted in filtering
    #print(tid)
    try:
        tid = (tid - tid[0]) / 1000.0
    except Exception as e:
        print(f"Error when loading graph data, exiting.")
        print(f"Error: {e}")
        
        exit(1)
    

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

    mask_time = (tid <= stop_time) & (tid >= start_time)
    t_zoom = tid[mask_time]
    adc_zoom = adc_detr[mask_time]

    ecg_bp = filtfilt(b, a, adc_zoom)
    
    return t_zoom, ecg_bp

# Try to detect R-peaks in a cleaned up ECG measurement
def detect_r_peaks(t, adc, rf_sec=0.25, thresh_factor=10.0):
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
    max_neg = min(adc_centered)
    
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
    #print("Noise_level: ", noise_level)
    
    if noise_level == 0:
        noise_level = 0.000001
        
    threshold = thresh_factor * noise_level
    
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
def analyze_ecg(filepath, rf_sec=0.25, thresh_factor=9):
    t, adc = filter_raw_ecg("recv_data.csv")
    
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
    
    
    
    
    