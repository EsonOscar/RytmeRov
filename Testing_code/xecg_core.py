import numpy as np # arbejder arrays matematik og signalbehandling 
from scipy.signal import butter, filtfilt # her henter vi butter som bruges til at fjerne uønskede frekvenser og filtfilt filtererer forlæs og baglæns
import statistics as stats
from sys import exit

# Take a raw ECG measurement and make it oh so beautiful 
def filter_raw_ecg(filepath, start_time=0, stop_time=10):
    """
    Takes a raw unfiltered ECG measurement containing times in ms, ADC values, LOP and LOM (electrode contact)
    and filters it, to produce a two clean output lists, t and adc.
    """
    #tomme lister 
    adc = [] 
    tid = []
    lom = []
    lop = []

    count = 0
    
    with open(filepath, "r") as f: #åbner filen
        for line in f: #går gennem hver linje du 
            #print(count)
            if count == 0: 
                pass
            else:       
                clean = line.strip() # fjerner mellemrum 
                data = clean.split(",") # deler ved komma 
                tid.append(int(data[0])) # tiden 
                adc.append(int(data[1])) # rå adc værdi 
                lom.append(int(data[2])) # status på eletroder 
                lop.append(int(data[3])) # status på eletroder 
            count = count + 1
    
    #print(tid)  
    #her convertere vi over til np array som bruges til matematik delen 
    tid = np.array(tid) 
    tid_ms = np.array(tid)
    adc =  np.array(adc)
    lom =  np.array(lom)
    lop =  np.array(lop)


    mask = (lom == 0) & (lop == 0) # her fortæller vi begge elektroder skal være 0 eller så virker lortet ik
    tid  = tid[mask] #her bliver 2 variabler fortalt, de kun skal behlde samples hvor begge elektrooder er iorden 
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
    
    
    adc_mean = adc.mean() # tage vi gennem gennemsnits værdien af adc'en 
    adc_detr = adc - adc_mean # 

    dt = np.diff(tid_ms) / 1000.0 #  er det forskellen mellem ode tidstempler, og gør dem til seconder 

    dt_med = np.median(dt) # så tager mdianen for at gøre det mere ordenlig gennemsnit
    fs = 1.0 / dt_med # fortæller hvor mange målninger vi får pr sek kan sige hvor hurtigt vi tager billede af signalet 
    
    # Design a 4th order Butterworth bandpass
    lowcut = 0.5   # fortælelr hvilke værdi vi gemme imellem Hz
    highcut = 40.0 # Hz
    nyq = 0.5 * fs # en formel til den hurtigest vi kan forstå signalet 
    low = lowcut / nyq #
    high = highcut / nyq

    b, a = butter(N=4, Wn=[low, high], btype='bandpass')  #design af vores buttterworth filter 

    mask_time = (tid <= stop_time) & (tid >= start_time) 
    t_zoom = tid[mask_time]
    adc_zoom = adc_detr[mask_time]

    ecg_bp = filtfilt(b, a, adc_zoom)
    
    return t_zoom, ecg_bp

# Try to detect R-peaks in a cleaned up ECG measurement
def detect_r_peaks(t, adc, rf_sec=0.25, thresh_factor=10.0): 
    
    """
    t = tid i sec, adc= filteret ekg signal, 
    rf_sec= refraztory periode som er mimum tid mellem peaks 
    threst_factor er hvor hård den skal være i forhold til støjniveau så jo højere tal jo færre peaks 
    Takes a cleaned up ECG measurement and tries to detect the R peaks of the QRS complex.
    """
    
    if len(adc) < 3: # færre end tre punkter levere tom liste 
        return []
    
    baseline = stats.median(adc) #tager median af signalet, 
    
    adc_centered = [] # oprette tom liste til 
    for val in adc: # 
        adc_centered.append(val - baseline) # her tager vi median og - den reale målning så vi får mere overskuelige tal 
    
    max_pos = max(adc_centered) # laver en variabler til max værdi postive 
    max_neg = min(adc_centered) # variable til størst negatvie værdig 
    
    #print(max_pos, max_neg)
    
    adc_final = [] 
    if abs(max_neg) > abs(max_pos): 
    # her tjekker vis så hvilken der størst hvis det R-peaks er posetive
    # vil max være stort og omvendt vil neg havde største abselut værdi
        for val in adc_centered:
            #hvis negativ har større værdig vender vi det om så vi slipper for at på tænke på om kurven vender op eller ned 
            adc_final.append(-val)
    else:
        adc_final = adc_centered
    
    abs_vals = [] # tom liste til abselutværdig 
    for val in adc_final:
        abs_vals.append(abs(val)) # putter vi værdi ved brug af vores beregning i abs 
        
    noise_level = stats.median(abs_vals) # her bruger vi vores abselute værdi som en typisk støjstyrk 
    #print("Noise_level: ", noise_level)
    
    if noise_level == 0:
        noise_level = 0.000001 # vi laver den her for at undgå at threshhold bliver 0 
    
    """ 
    her laver vi vores threshold som lige som hjælper til holde styr på om det realt er et hjertslag
    iv har sat den til den skal være 10 gange større fir det tæller for et R-peak hvilket vi beregner her. 
    """
    threshold = thresh_factor * noise_level 
    
    #print("Threshold: ", threshold)
    
    r_indices = [] # tom liste til hvert R-peak 
    last_peak_time = -1000000000 # bruges til at sikre først peak altid bliver godkendt 
    
    """
    her kommer vores loop som er her vi beregner hver vores peaks 
    """
    for i in range(1, len(adc_final) - 1):
        if adc_final[i] > adc_final[i - 1] and adc_final[i] >= adc_final[i + 1]:
            if adc_final[i] >= threshold: # kun hvis peaket er stort nok 
                if t[i] - last_peak_time >= rf_sec: #tid for for nuværende peak  og forskellen er større eller lig med 
                    r_indices.append(i) #
                    last_peak_time = t[i] # opdatere  tiden 
                    
    #print("Number of peaks found: ", len(r_indices))
    #print(r_indices)
    
    return r_indices, noise_level # returner liste med hvor der funder R-peaks og noise_level 


# Final put together version, with data like HR, intervals etc. pretty cool good job Oscar
def analyze_ecg(filepath, rf_sec=0.25, thresh_factor=9):
    t, adc = filter_raw_ecg("recv_data.csv") # henter den tidligere funktion her henter vi t og adc 
    
    if len(t) == 0: #lille fall back hvis der ikke er nogle målninger returnere den none 
        print("No values in the selected dataset")
        return None

    # kan man sige vi samler antallet af beats her 
    r_indices, noise_level = detect_r_peaks(t, adc, rf_sec, thresh_factor) 
    beats = len(r_indices) #putter dem i en variable 
    
    # hvis der er ikke er nok beats, vil den returet none 
    if beats < 2:
        print("Not enough beats in the selected dataset")
        return None

    
    r_times = [] #tom liste  til vores vores tider med R-peaks 

    for val in r_indices: # mangler kommentar 
        r_times.append(t[val])
    
    #print(r_times)
    
    rr = [] # 
    """
    den her tager beat og deres timestamp og sammenligner med hinaden 
    for se det mellem rummet af tid, om det passer til hvad man forventer
    """
    for i in range(beats -1):
        rr.append(r_times[i + 1] - r_times[i])
    
    #print(len(rr))
    #print(rr)
    
    rr_mean = stats.mean(rr) #tager gennemsnittet af alle RR-intervaller 
    #print(rr_mean)
    

    hr_per_interval = [] 
    for val in rr: # 
        if val == 0: # tjekker hvis nul for sikre at man ikke rammer 0 devision 
            break
        else:
            hr_per_interval.append(60 / val) # så tjekker vi puls ved hvert slag 

    #print(hr_per_interval)
    # laver en fall back hvis, målningerne er 0 
    if rr_mean != 0:
        hr_mean = 60 / rr_mean
    else:
        hr_mean = None 
    # her beregner vi standard afvigelsen, og har en fallback, hvis der kun er 1,
    if len(rr) > 1:
        rr_std = stats.pstdev(rr) # hvis rr_std har stor varation kan det tyde på hjertflimmer 
    else:
        rr_std = None
        
    # skal her får vi fucking bare alt retur 
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
    # filtrer til ekg 
    t, adc = filter_raw_ecg("recv_data.csv")
    print("\nFile has been cleaned up, remaining t and adc indices:")
    print(len(t), len(adc), "\n")
    
    #finder vores R-peaks 
    r_peaks = detect_r_peaks(t, adc)
    print("Number of R-peaks found:")
    print(len(r_peaks), "\n")
    
    #kør samlet analyse 
    result = analyze_ecg("recv_data.csv")
    
    if result is not None: 
        print("Analyzed data:")
        print("Found beats:", result.get("beats"))
        print("Average heartrate:", round(result.get("hr_mean"), 2), "beats per minute")
        print("Average RR interval:", round(result.get("rr_mean"), 2), "seconds")
        print("RR intervals standard deviation:", result.get("rr_std"))
        print("Noise level:", result.get("noise"))
        print("Thank the fucking Lord Oscar Ericson for his genius math skills, amen.")
    else: 
        print("cg analysen failed (ikke not data eller R-peaks )")
   

    