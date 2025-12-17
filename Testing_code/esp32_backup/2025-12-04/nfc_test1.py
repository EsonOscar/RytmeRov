from machine import Pin, SPI
import time
import NFC_PN532 as nfc

# --- Optional: reset PN532 into SPI mode ---
# If your board has a RESET pin, wire it to e.g. GPIO27
try:
    rst = Pin(27, Pin.OUT)
    rst.value(0)
    time.sleep(0.1)
    rst.value(1)
    time.sleep(0.5)  # let PN532 boot into SPI
except Exception:
    # If you didn't wire reset, just ignore this
    pass

# --- SPI setup (VSPI on ESP32) ---
spi = SPI(
    2,                    # VSPI (id=2) on ESP32
    baudrate=1_000_000,   # 1 MHz is plenty for PN532
    polarity=0,
    phase=0,
    sck=Pin(18),
    mosi=Pin(23),
    miso=Pin(19),
)

cs = Pin(5, Pin.OUT)
cs.on()  # deselect chip by default

# --- Init PN532 driver ---
pn532 = nfc.PN532(spi, cs)

# Get firmware version
ic, ver, rev, support = pn532.get_firmware_version()
print("Found PN532 with firmware version: {}.{}".format(ver, rev))

# Put it into "normal" mode for MiFare tags
pn532.SAM_configuration()

def read_uid_once(timeout_ms=500):
    #print("Waiting for card...")
    uid = pn532.read_passive_target(timeout=timeout_ms)
    if uid is None:
        #print("No card detected")
        return
    
    data = pn532.mifare_classic_read_block(1)
    
    print("\nRaw UID bytes:", uid)
    print("UID hex:", ":".join("{:02X}".format(b) for b in uid))
    # If you want a simple decimal string form:
    nums = [int(b) for b in uid]
    print("UID decimal tuple:", nums)
    print(f"Data: {data}")
    
#def read_data(timeout_ms=500):

while True:
    read_uid_once()
    time.sleep(0.5)
