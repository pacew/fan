import argparse
import sys


for b in pkt1:
    print(f'{b:02x}', end=' ')
print()
for b in pkt2:
    print(f'{b:02x}', end=' ')
print()



sys.exit(0)




import cc1101
import time
import sys

# it works with frequences in this range
freq_range = [303e6, 307e6]
freq = sum(freq_range) / len(freq_range)


    



# get these numbers with
# rtl_433 -f 303.733M -X "n=fan,m=OOK_PCM,s=332,l=332,r=2000"
codes = {
    'light-toggle': [
        bytes([0xb2, 0x49, 0x64, 0x92, 0x58]),
        bytes([0xb2, 0x49, 0x64, 0x92, 0x48])
    ],
    'fan-off': [
        bytes([0xb2, 0x49, 0x64, 0x92, 0xc8]),
        bytes([0xb2, 0x49, 0x64, 0x92, 0x48]),
    ],
    'fan-low': [
        bytes([0xb2, 0x49, 0x64, 0xb2, 0x48]),
        bytes([0xb2, 0x49, 0x64, 0x92, 0x48]),
    ],
    'fan-med': [
        bytes([0xb2, 0x49, 0x65, 0x92, 0x48]),
        bytes([0xb2, 0x49, 0x64, 0x92, 0x48]),
    ],
    'fan-high': [
        bytes([0xb2, 0x49, 0x6c, 0x92, 0x48]),
        bytes([0xb2, 0x49, 0x64, 0x92, 0x48]),
    ],
}


def xmit(pkts):
    with cc1101.CC1101() as transceiver:
        transceiver.set_base_frequency_hertz(freq)
        transceiver.set_symbol_rate_baud(3035)
        transceiver.set_sync_mode(cc1101.SyncMode.NO_PREAMBLE_AND_SYNC_WORD)
        transceiver.set_packet_length_mode(cc1101.PacketLengthMode.FIXED)
        transceiver.disable_checksum()
        transceiver.set_output_power((0, 0xC0))  # OOK modulation: (off, on)

        for pkt in pkts:
            transceiver.set_packet_length_bytes(len(pkt))

            for _ in range(6):
                transceiver.transmit(pkt)
                time.sleep(0.03)

class Builder:
    def __init__(self):
        self.reset()

    def reset(self):
        self.pkt = []
        self.bitnum = 7
        self.byte = 0

    def append(self, val):
        self.byte |= val << self.bitnum
        if self.bitnum > 0:
            self.bitnum -= 1
        else:
            self.pkt.append(self.byte)
            self.bitnum = 7
            self.byte = 0
            
    def get(self):
        if self.bitnum != 7:
            self.pkt.append(self.byte)
        val = bytes(self.pkt)
        self.reset()
        return val

def make_cmd(args):
    pkt = Builder()

    def add_val(val):
        pkt.append(1)
        pkt.append(0)
        pkt.append(1 if val != 0 else 0)

    add_val(1)
    dip = int(args.dip)
    add_val(dip & 8)
    add_val(dip & 4)
    add_val(dip & 2)
    add_val(dip & 1)
    add_val(1)
    add_val(1 if args.op == 'high' else 0)
    add_val(1 if args.op == 'med' else 0)
    add_val(1 if args.op == 'low' else 0)
    add_val(0)
    add_val(1 if args.op == 'off' else 0)
    add_val(1 if args.op == 'light' else 0)
    add_val(0)
    return pkt.get()

parser = argparse.ArgumentParser()
parser.add_argument('--dip', default='0')
parser.add_argument('op')

args = parser.parse_args()

pkt1 = make_cmd(args)

# make "all up" code
args.op = None
pkt2 = make_cmd(args)

xmit([pkt1, pkt2])



        

