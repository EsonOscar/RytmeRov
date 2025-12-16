import numpy as np
from scipy.signal import butter, filtfilt
import statistics as stats
from sys import exit


# 1️⃣ DATAINDLÆSNING ---------------------------------------------------------

def load_ecg_csv(filepath):
    """
    Læser rå ECG-data fra en CSV-fil.

    Forventet format (med header):
        tid_ms, adc, lom, lop

    Returnerer:
        t_ms : np.ndarray (ms)
        adc  : np.ndarray (rå ADC)
        lom  : np.ndarray (elektrode-status)
        lop  : np.ndarray (elektrode-status)
    """
    t_ms, adc, lom, lop = [], [], [], []

    try:
        with open(filepath, "r") as f:
            # Spring headerlinje over
            next(f)

            for line in f:
                clean = line.strip()
                if not clean:
                    continue

                data = clean.split(",")
                if len(data) < 4:
                    # Ufuldstændig linje → spring over
                    continue

                t_ms.append(int(data[0]))
                adc.append(int(data[1]))
                lom.append(int(data[2]))
                lop.append(int(data[3]))

    except FileNotFoundError:
        print(f"Fejl: Kunne ikke finde filen '{filepath}'.")
        return None, None, None, None

    if len(t_ms) == 0:
        print("Fejl: Ingen data læst fra filen.")
        return None, None, None, None

    return (
        np.array(t_ms, dtype=float),
        np.array(adc, dtype=float),
        np.array(lom, dtype=int),
        np.array(lop, dtype=int),
    )


# 2️⃣ SIGNALBEHANDLING / PREPROCESSING ---------------------------------------

def preprocess_ecg(t_ms, adc, lom, lop, start_time=0.0, stop_time=10.0):
    """
    Rydder op i ECG-data:
      - fjerner samples med dårlige elektroder
      - konverterer ms → sekunder
      - fjerner DC-offset
      - laver bandpas-filtrering (0.5–40 Hz)
      - vælger et tidsvindue (start_time → stop_time)

    Returnerer:
        t_zoom   : np.ndarray (sekunder)
        ecg_bp   : np.ndarray (filtreret signal)
        fs       : float (samplingfrekvens i Hz)
    """
    # Filtrér samples med begge elektroder OK (0 = OK)
    mask_ok = (lom == 0) & (lop == 0)
    t_ms = t_ms[mask_ok]
    adc = adc[mask_ok]

    if len(t_ms) < 3:
        print("Fejl: For få brugbare samples efter elektrodefiltrering.")
        return None, None, None

    # Tid i sekunder, start ved 0
    try:
        t_sec = (t_ms - t_ms[0]) / 1000.0
    except Exception as e:
        print("Fejl under behandling af tidsdata.")
        print(f"Error: {e}")
        exit(1)

    # Fjern DC-offset
    adc_mean = adc.mean()
    adc_detr = adc - adc_mean

    # Estimér samplingfrekvens
    dt = np.diff(t_sec)
    dt_med = np.median(dt)
    if dt_med <= 0:
        print("Fejl: Ugyldige tidsskridt, kan ikke beregne samplingfrekvens.")
        return None, None, None

    fs = 1.0 / dt_med

    # Definér bandpasfilter 0.5–40 Hz
    lowcut = 0.5
    highcut = 40.0
    nyq = fs / 2.0

    low = lowcut / nyq
    high = highcut / nyq

    if not (0 < low < 1) or not (0 < high < 1):
        print("Fejl: Filtergrænser giver ikke mening med den aktuelle samplingfrekvens.")
        return None, None, None

    b, a = butter(N=4, Wn=[low, high], btype="bandpass")

    # Vælg tidsvindue
    mask_time = (t_sec >= start_time) & (t_sec <= stop_time)
    t_zoom = t_sec[mask_time]
    adc_zoom = adc_detr[mask_time]

    if len(t_zoom) < 3:
        print("Fejl: Ingen eller for få samples i det valgte tidsvindue.")
        return None, None, None

    # Filtrér signalet (frem og tilbage)
    ecg_bp = filtfilt(b, a, adc_zoom)

    return t_zoom, ecg_bp, fs


# 3️⃣ R-PEAK DETEKTION -------------------------------------------------------

def detect_r_peaks(t, adc, rf_sec=0.25, thresh_factor=10.0):
    """
    Finder R-peaks i et filtreret ECG-signal.

    Parametre:
        t            : np.ndarray, tid i sekunder
        adc          : np.ndarray, filtreret ECG
        rf_sec       : refraktærperiode (minimum tid mellem to peaks)
        thresh_factor: threshold-faktor ift. støjniveau

    Returnerer:
        r_indices   : liste med indeks for R-peaks i adc/t
        noise_level : estimeret støjniveau (median(|signal|))
    """
    if t is None or adc is None or len(adc) < 3:
        return [], 0.0

    # Flyt signalet omkring 0 ved at bruge median som baseline
    baseline = stats.median(adc)
    adc_centered = np.array(adc) - baseline

    max_pos = float(np.max(adc_centered))
    max_neg = float(np.min(adc_centered))

    # Sørg for at R-peaks er positive (vend evt. signalet)
    if abs(max_neg) > abs(max_pos):
        adc_final = -adc_centered
    else:
        adc_final = adc_centered

    abs_vals = np.abs(adc_final)
    noise_level = stats.median(abs_vals)

    if noise_level == 0:
        noise_level = 1e-6  # undgå threshold = 0

    threshold = thresh_factor * noise_level

    r_indices = []
    last_peak_time = -1e9  # sikrer at første peak altid kan godkendes

    # Søg efter lokale maxima over threshold
    for i in range(1, len(adc_final) - 1):
        if adc_final[i] > adc_final[i - 1] and adc_final[i] >= adc_final[i + 1]:
            if adc_final[i] >= threshold:
                if t[i] - last_peak_time >= rf_sec:
                    r_indices.append(i)
                    last_peak_time = t[i]

    return r_indices, noise_level


# 4️⃣ ANALYSELOGIK (RR, HR, osv.) -------------------------------------------

def analyze_ecg_signal(t, ecg, rf_sec=0.25, thresh_factor=9.0):
    """
    Laver samlet analyse af et filtreret ECG-signal.

    Input:
        t     : tid i sekunder (np.ndarray)
        ecg   : filtreret ECG (np.ndarray)

    Returnerer en dict:
        {
            "beats": antal slag,
            "r_peak_times": liste med tidspunkter,
            "rr_intervals": liste med RR-interval i sekunder,
            "rr_mean": gennemsnitligt RR-interval (sek),
            "rr_std": standardafvigelse for RR,
            "hr_mean": gennemsnitspuls (bpm),
            "hr_per_interval": liste med HR for hvert interval,
            "noise": støjniveau
        }
    """
    r_indices, noise_level = detect_r_peaks(t, ecg, rf_sec, thresh_factor)
    beats = len(r_indices)

    if beats < 2:
        print("Der er ikke nok slag til at lave en ordentlig analyse.")
        return None

    # Tidspunkter for R-peaks
    r_times = t[r_indices]

    # RR-intervaller (sekunder mellem to slag)
    rr = np.diff(r_times)

    if len(rr) == 0:
        print("Kun ét RR-interval fundet, for lidt data.")
        return None

    rr_mean = float(rr.mean())
    rr_std = float(rr.std())

    # HR for hvert interval
    hr_per_interval = []
    for val in rr:
        if val > 0:
            hr_per_interval.append(60.0 / val)

    if rr_mean > 0:
        hr_mean = 60.0 / rr_mean
    else:
        hr_mean = None

    return {
        "beats": beats,
        "r_peak_times": r_times.tolist(),
        "rr_intervals": rr.tolist(),
        "rr_mean": rr_mean,
        "rr_std": rr_std,
        "hr_mean": hr_mean,
        "hr_per_interval": hr_per_interval,
        "noise": noise_level,
    }


# 5️⃣ RYTME-VURDERING -------------------------------------------------------

def test_rytme_analyse(result):
    """
    Vurderer hjerterytmen ud fra HR og variation i RR-intervaller.
    Returnerer en beskrivende tekst.
    """
    if result is None:
        return "Der er ingen data til at analysere."

    hr_mean = result.get("hr_mean")
    rr_mean = result.get("rr_mean")
    rr_std = result.get("rr_std")
    beats = result.get("beats")

    # Fallback hvis der mangler noget
    if hr_mean is None or rr_mean is None or rr_std is None or beats is None:
        return "Ikke nok data til at vurdere hjerterytmen."

    if beats < 3:
        return "Der er for få slag til at vurdere rytmen, prøv at måle længere tid."

    # Variationskoefficient (CV) for RR-intervaller
    if rr_mean > 0:
        cv_rr = rr_std / rr_mean
    else:
        cv_rr = 0.0

    print(
        f"DEBUG rhythm: hr_mean={hr_mean:.1f}, "
        f"rr_mean={rr_mean:.3f}, rr_std={rr_std:.3f}, "
        f"cv_rr={cv_rr:.3f}, beats={beats}"
    )

    if cv_rr < 0.05:
        return (
            f"Rytmen ser regelmæssig ud. "
            f"Gennemsnitspulsen ligger på {hr_mean:.1f} bpm."
        )
    elif cv_rr <= 0.20:
        return (
            f"Rytmen er overordnet regelmæssig med fin variation i slagene. "
            f"Patientens gennemsnitspuls = {hr_mean:.1f} bpm."
        )
    else:
        return (
            f"Rytmen virker uregelmæssig med stor variation i RR-intervallerne. "
            f"Patientens gennemsnitspuls = {hr_mean:.1f} bpm."
        )


# 6️⃣ MAIN – SAMLER ALT -----------------------------------------------------

def main():
    filepath = "recv_data.csv"

    # 1) Hent rå data
    t_ms, adc, lom, lop = load_ecg_csv(filepath)
    if t_ms is None:
        return

    # 2) Preprocess (filtrering osv.)
    t, ecg, fs = preprocess_ecg(t_ms, adc, lom, lop, start_time=0.0, stop_time=10.0)
    if t is None:
        return

    print("\nFil er læst og renset.")
    print("Antal samples efter filtrering:", len(t))
    print(f"Estimeret samplingfrekvens: {fs:.1f} Hz\n")

    # 3) Analyse af det filtrerede signal
    result = analyze_ecg_signal(t, ecg)
    if result is None:
        print("Analysen kunne ikke gennemføres.")
        return

    print("Analyserede data:")
    print("  Fundne beats:", result.get("beats"))
    print("  Gennemsnitspuls:", round(result.get("hr_mean"), 2), "bpm")
    print("  Gennemsnitligt RR-interval:", round(result.get("rr_mean"), 3), "sek")
    print("  Standardafvigelse for RR:", round(result.get("rr_std"), 3))
    print("  Estimeret støjniveau:", result.get("noise"))

    # 4) Rytme-vurdering
    vurdering = test_rytme_analyse(result)
    print("\nTeknisk rytme-vurdering:")
    print(vurdering)


if __name__ == "__main__":
    main()
