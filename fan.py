import argparse
import cc1101
import time
import sys

# it works with frequences in this range
freq_range = [303e6, 307e6]
freq = sum(freq_range) / 2  # use the average of the extremes

# 3035 measured
baud_range = [2170, 3500]
baud = sum(baud_range) / 2

# for power, 0xc0 is example in the python library
# the data sheet mentions values between 3 and 0xcc
# at a range of 20 feet 0x33 was marginal, 0x34 was reliable
# so 0xc0 is about maximum, no reason not to use that

def xmit(pkts):
    with cc1101.CC1101() as transceiver:
        transceiver.set_base_frequency_hertz(freq)
        transceiver.set_symbol_rate_baud(baud)
        transceiver.set_sync_mode(cc1101.SyncMode.NO_PREAMBLE_AND_SYNC_WORD)
        transceiver.set_packet_length_mode(cc1101.PacketLengthMode.FIXED)
        transceiver.disable_checksum()

        # OOK modulation: (off, on)
        transceiver.set_output_power((0, 0xc0))  

        for pkt in pkts:
            transceiver.set_packet_length_bytes(len(pkt))

            for _ in range(6):
                transceiver.transmit(pkt)
                while (transceiver.get_marc_state() !=
                       cc1101.MainRadioControlStateMachineState.IDLE):
                    time.sleep(0.01)

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
    ops = args.op.split(' ')

    pkt = Builder()

    def add_val(val):
        pkt.append(1)
        pkt.append(0)
        pkt.append(1 if val != 0 else 0)

    # if you send light and off in the same pkt, nothing happens
    #
    # if you send light and a fan motion in the same pkt, it
    # executes just the light
    #
    # if you send multiple motions, nothing happens
    #
    # if you repeat the light command for more than about a half
    # second, it starts cycling the brightness, but there's no
    # way to know the current brightness
    add_val(1)
    dip = int(args.dip)
    add_val(dip & 8)
    add_val(dip & 4)
    add_val(dip & 2)
    add_val(dip & 1)
    # if the light bit is also on, 0 means bright, 1 respects dimmer
    # ignored for motion command
    # real remotes always send 1
    add_val(0 if 'bright' in ops else 1)
    add_val(1 if 'high' in ops else 0)
    add_val(1 if 'med' in ops else 0)
    add_val(1 if 'low' in ops else 0)
    # unknown function for this bit. real remotes always send 0
    # if you send 1, nothing appears to happen, and it
    # prevents any other 1 bit from being recognized
    add_val(1 if 'extra' in ops else 0)  # real remotes send 0
    add_val(1 if 'off' in ops else 0)
    add_val(1 if 'light' in ops else 0)
    add_val(0)  # end marker
    return pkt.get()

parser = argparse.ArgumentParser()
parser.add_argument('--dip', default='0')
parser.add_argument('op')

args = parser.parse_args()

pkts = [make_cmd(args)]

if False:
    # the real remotes send an "all up" code
    args.op = None
    pkts.append = make_cmd(args)

xmit(pkts)



        

