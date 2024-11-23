import cc1101
import time
import sys

# printf '\x20\x81' | cc1101-transmit -f 303725000 -r 1000 ^C
# can be seen by rtl_433 -f 303.725M -A

# get these numbers with
# rtl_433 -f 303.725M -X "n=fan,m=OOK_PCM,s=332,l=332,r=2000"
codes = {
    'light-toggle': [
        bytes([0xb2, 0x49, 0x64, 0x92, 0x58]),
        bytes([0xb2, 0x49, 0x64, 0x92, 0x50])
    ],
    'fan-off': [
        bytes([0xb2, 0x49, 0x64, 0x92, 0xc8]),
        bytes([0xb2, 0x49, 0x64, 0x92, 0x48]),
    ],
    'fan-low': [
        bytes([0xb2, 0x49, 0x64, 0xb2, 0x48]),
        bytes([0xb2, 0x49, 0x64, 0x92, 0x48]),
    ],
    'fan-high': [
        bytes([0xb2, 0x49, 0x6c, 0x92, 0x48]),
        bytes([0xb2, 0x49, 0x64, 0x92, 0x48]),
    ],
}


def xmit(button):
    freq = 303.725e6 + 28000
    with cc1101.CC1101() as transceiver:
        transceiver.set_base_frequency_hertz(freq)
        transceiver.set_symbol_rate_baud(3035)
        transceiver.set_sync_mode(cc1101.SyncMode.NO_PREAMBLE_AND_SYNC_WORD)
        transceiver.set_packet_length_mode(cc1101.PacketLengthMode.FIXED)
        transceiver.set_packet_length_bytes(5)
        transceiver.disable_checksum()
        transceiver.set_output_power((0, 0xC0))  # OOK modulation: (off, on)
        # transceiver.enable_manchester_code()
        print(transceiver)

        try:
            code = codes[button]
        except KeyError:
            print('unknown button', button)
            sys.exit(1)

        for _ in range(6):
            transceiver.transmit(code[0])
            time.sleep(0.02)
        if code[1]:
            for _ in range(2):
                transceiver.transmit(code[1])
                time.sleep(0.02)

xmit(sys.argv[1])


        

