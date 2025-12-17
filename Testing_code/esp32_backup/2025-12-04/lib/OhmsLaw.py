#Ohms law calculation
#Prints results, optionally returns result

from math import sqrt

class OhmsLawCalc:
    
    #Constructor
    def __init__(self):
        self.voltage = None
        self.current = None
        self.resistance = None
        self.power = None
        
    #Readme function
    def readme(self):
        print("Functions in OhmsLawCalc.py:\n")
        
        print("Power funcitons:")
        print("*.powerIR(CURRENT, RESISTANCE)	| Calculates power, using current and resistance.")
        print("*.powerUR(VOLTAGE, RESISTANCE)	| Calculates power, using voltage and resistance.")
        print("*.powerUI(VOLTAGE, CURRENT)	| Calculates power, using voltage and current.\n")
        
        print("Current functions:")
        print("*.currentUR(VOLTAGE, RESISTANCE)| Calculates current, using voltage and resistance.")
        print("*.currentPU(POWER, VOLTAGE)	| Calculates current, using power and voltage.")
        print("*.currentPR(POWER, RESISTANCE)	| Calculates current, using power and resistance.\n")
        
        print("Resistance functions:")
        print("*.resistanceUP(VOLTAGE, POWER)	| Calculates resistance, using voltage and power.")
        print("*.resistanceUI(VOLTAGE, CURRENT)| Calculates resistance, using voltage and current.")
        print("*.resistancePI(POWER, CURRENT)	| Calculates resistance, using power and current.\n")
        
        print("Voltage functions:")
        print("*.voltageRI(RESISTANCE, CURRENT)| Calculates voltage, using resistance and current.")
        print("*.voltagePR(POWER, RESISTANCE)	| Calculates voltage, using power and resistance.")
        print("*.voltagePI(POWER, CURRENT)	| Calculates voltage, using power and current.\n")

############################################################################  

    #Power functions
    def powerIR(self, current, resistance):
        self.current = current
        self.resistance = resistance
        
        self.power = (self.current ** 2) * self.resistance
        print(f"Power: {self.power} W\n")
        
        return self.power
    
    def powerUR(self, voltage, resistance):
        self.voltage = voltage
        self.resistance = resistance
        
        self.power = (self.voltage ** 2) / self.resistance
        print(f"Power: {self.power} W\n")
        
        return self.power
        
    def powerUI(self, voltage, current):
        self.voltage = voltage
        self.current = current
        
        self.power = self.voltage * self.current
        print(f"Power: {self.power} W\n")
        
        return self.power
        
############################################################################        
    
    #Current functions
    def currentUR(self, voltage, resistance):
        self.voltage = voltage
        self.resistance = resistance
        
        self.current = self.voltage / self.resistance
        print(f"Current: {self.current} A\n")
        
        return self.current
        
    def currentPU(self, power, voltage):
        self.power = power
        self.voltage = voltage
        
        self.current = self.power / self.voltage
        print(f"Current: {self.current} A\n")
        return self.current
    
    def currentPR(self, power, resistance):
        self.power = power
        self.resistance = resistance
        
        self.current = sqrt(self.power/self.resistance)
        print(f"Current: {self.current} A\n")
        return self.current
        
############################################################################
    
    #Resistance functions
    def resistanceUP(self, voltage, power):
        self.voltage = voltage
        self.power = power
        
        self.resistance = (self.voltage ** 2) / self.power
        print(f"Resistance: {self.resistance} Ω\n")
        return self.resistance
    
    def resistanceUI(self, voltage, current):
        self.voltage = voltage
        self.current = current
        
        self.resistance = self.voltage / self.current
        print(f"Resistance: {self.resistance} Ω\n")
        return self.resistance
    
    def resistancePI(self, power, current):
        self.power = power
        self.current = current
        
        self.resistance = self.power / (self.current ** 2)
        print(f"Resistance: {self.resistance} Ω\n")
        return self.resistance
    
############################################################################
    
    #Voltage functions
    def voltageRI(self, resistance, current):
        self.resistance = resistance
        self.current = current
        
        self.voltage = self.resistance * self.current
        print(f"Voltage: {self.voltage} V\n")
        return self.voltage
    
    def voltagePR(self, power, resistance):
        self.power = power
        self.resistance = resistance
        
        self.voltage = sqrt(self.power * self.resistance)
        print(f"Voltage: {self.voltage} V\n")
        return self.voltage
    
    def voltagePI(self, power, current):
        self.power = power
        self.current = current
        
        self.voltage = self.power / self.current
        print(f"Voltage: {self.voltage} V\n")
        return self.voltage
    
############################################################################ 