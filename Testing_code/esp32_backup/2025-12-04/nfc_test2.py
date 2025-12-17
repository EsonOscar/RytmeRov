import NFC_PN532 as nfc
from machine import Pin, SPI
import time

# --- your existing init ---
spi = SPI(
    2,
    baudrate=1_000_000,
    polarity=0,
    phase=0,
    sck=Pin(18),
    mosi=Pin(23),
    miso=Pin(19),
)
cs = Pin(5, Pin.OUT)
cs.on()
pn532 = nfc.PN532(spi, cs)
pn532.SAM_configuration()

def dump_mifare_1k():
    print("Waiting for MIFARE Classic card...")
    uid = pn532.read_passive_target(timeout=1000)
    if uid is None:
        print("No card detected")
        return

    print("Card UID:", ":".join("{:02X}".format(b) for b in uid))

    # MIFARE Classic 1K has 16 sectors × 4 blocks = 64 blocks (0–63)
    for block in range(0, 64):
        # Authenticate this block with default key B (FF FF FF FF FF FF)
        ok = pn532.mifare_classic_authenticate_block(
            uid,
            block,
            key=nfc.KEY_DEFAULT_B,  # defined in NFC_PN532.py
        )

        if not ok:
            print("Block {:02d}: auth FAILED".format(block))
            continue

        data = pn532.mifare_classic_read_block(block)
        if data is None:
            print("Block {:02d}: read FAILED".format(block))
            continue

        # Print as hex and ASCII-ish
        hex_str = " ".join("{:02X}".format(b) for b in data)
        ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in data)
        print("Block {:02d}: {}   |{}|".format(block, hex_str, ascii_str))

while True:
    dump_mifare_1k()
    print("----")
    time.sleep(2)
