import cc1101
import time

# printf '\x20\x81' | cc1101-transmit -f 303725000 -r 1000 ^C
# can be seen by rtl_433 -f 303.725M -A


freq = 303.725e6 + 28000
# freq = 433.92e6
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
    for _ in range(6):
        transceiver.transmit(bytes([0b10110010,
                                    0b01001001,
                                    0b01100100,
                                    0b10010010,
                                    0b01011000,
                                    ]))
        time.sleep(0.02)
    for _ in range(2):
        transceiver.transmit(bytes([0b10110010,
                                    0b01001001,
                                    0b01100100,
                                    0b10010010,
                                    0b01010000,
                                    ]))
        time.sleep(0.02)

        

