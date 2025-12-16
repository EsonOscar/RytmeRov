from xecg_core import analyze_ecg # vi tester ny metoder hvor vi importere fra dada oscars flotte krop 
# list til overblik for folk der har ikke kigget denne kode 
"""
    "beats": beats,                     antal R-peaks (hjerteslag)
    "r_indices": r_indices,             indekser hvor R-peaks findes i signalet
    "r_peak_times": r_times,            tidspunkter i sekunder for hvert R-peak
    "rr_intervals": rr,                 RR-intervaller: tid mellem to hjerteslag
    "rr_mean": rr_mean,                 gennemsnitligt RR-interval
    "rr_std": rr_std,                   variation i RR-intervaller (rytme-regularitet)
    "hr_mean": hr_mean,                 gennemsnitlig puls i bpm
    "hr_per_interval": hr_per_interval, puls for hvert enkelt slag
    "noise": noise_level                estimeret støjniveau i signalet
"""

def tester_rytme_analysen(filepath="recv_data.csv"):
    #tager den samllede analys 
    result = analyze_ecg(filepath)
    
    #hvis vi så får none så er det fordi der gik noget galt fallback 
    if result is None: 
        print("fik ikke nok data til lave en lorte analyse")
        return

    #henter vores data 

    beats = result.get("beats")
    rr_mean = result.get("rr_mean")#gennemsnits RR 
    rr_std = result.get("rr_std") # hvordan RR-intervalet varierer 
    hr_mean = result.get("hr_mean") #gennemsnits puls 

    
    print("\n--- RÅ EKG-ANALYSE ---")
    print(f"Antal beats: {beats}")
    print(f"Gennemsnitlig HR: {hr_mean:.1f} bpm")
    print(f"Gennemsnitligt RR-interval: {rr_mean:.3f} s")
    print(f"Standardafvigelse af RR: {rr_std}")

    rytme_type, vurdering_rytme, samlet_tekst = rytme_vurdering(rr_mean, rr_std, hr_mean)

    print("vudering")
    print("frekvens-vurdering:", rytme_type)
    print("Rytme vurdering", vurdering_rytme)
    print("samlet vurdering", samlet_tekst)

#funktion til 
def rytme_vurdering(rr_mean, rr_std, hr_mean): 

    #lige en lille fallback hvis der ikke er nok data 
    if rr_mean is None or rr_std is None or hr_mean is None:
        return (
            " det er ikke muligt at vurdere puls for lidt data"
            "mangler data til rytme vurdering"
            "mangler data til samlet vurdering"
            )


    if hr_mean <60: 
        rytme_type = "pulsen er lav hvilket betyder hjerte slår langsommere end normalt" # fagligt term man kunne putter ind her er bradykardi
    elif hr_mean > 100: 
        rytme_type = "pulsen er for høj" #fagligt term her er takykardi 
    else: 
        rytme_type = "pulsen er normal" # den normal mellem 60 og 100 slag 
    

    # her kommer vurdering af rytmen her bruger vi rr_st som er hvor stor variation der mellem hvert slag 
    if rr_std < 0.06: # bruger en if funktion til at fortælle hvis der kommer slag i mellem 0.06 og 12 er den regle mæssig 
        vurdering_rytme = "slagende ligger ens hvildet betyder der er en regelmæssig rytme "
    elif rr_std < 0.12: #alt over 12 fortolker vi som uregelmæssigt 
        vurdering_rytme="slagene ligger lettere uregelmøssigt"
    else: # alt over det er for store udsving hvilket så vil blive kataroseriet som hjerteflimmer 
        vurdering_rytme="der stor variation i slagene og man burde tage en ordenlig ekg analyse "
    
    # variable der samler begge typer data. 
    vurdering = f"{rytme_type}, og {vurdering_rytme}"
    
    return rytme_type, vurdering_rytme, vurdering


if __name__ == "__main__":
    tester_rytme_analysen("recv_data.csv")