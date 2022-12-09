#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# multimidiseq.py
#
# based on: drumseq.py
# from here: https://github.com/SpotlightKid/python-rtmidi/tree/master/examples/drumseq
# which is itself based on:
# MIDI Drum sequencer prototype, by Michiel Overtoom, motoom@xs4all.nl
#
"""Play sequencer patterns from file to MIDI out."""

import argparse
import sys

from multimidiseq import PatternSequencer as pseq
from multimidiseq import DrumPattern as dp

from time import sleep, time as timenow

from rtmidi.midiutil import open_midioutput, list_output_ports, list_input_ports
import rtmidi

# BD1 = BaseDrum1
# CHH = Closed Hi-hat
# OHH = Open Hi-hat
# SN1 = Snare1
# SN2 = Snare2
# CR1 = Crash1
# CR2 = Crash2
# RD1 = Ride1
# RD2 = Ride2
# CB1 = Cowbell1
# CP1 = Clap1
# TM1 = TOM1
# TM2 = TOM2
# TM3 = TOM3
# TM4 = TOM4

# Korg Wavestate Single Multisample: "Drm_WS: Drum Kit".
# On Wavestate Layer A: Octave +2 (so that you can use the keys
#                       on the Wavestate to play the other layers)
DRUMMIDIASSIGN_KorkWavestate_DrumKit = """
BD1 12
SN1 15
SN2 16
CHH 29
OHH 31
CR1 32
CB1 41
CP1 22
"""

FUTUREDRUMPATTERN1 = """
BD1 x.....s.x.......x.....m.x.......
SN1 ....m-......m-......m-......m-..
CHH xsssxsssxsssxsssxsssxsssxsssxsss
"""


# Wave Sequencing 2.0 Synth Pattern
WSSPATTERN1 = """"
BASENOTE 48
KEYUPLIMIT 50
KEYLOWLIMIT 48
TIMING  014 014 014 014 014 014 014 318 318 318
PITCH   --- --- --- --- --- --- --- 000 007 012
VEL     --- --- --- --- --- --- --- sss sss sss
"""

def selectInputPort():
    portnrstr = input("Select the input port by typing the corresponding number: ")
    selected_input_port = int(portnrstr)

    return selected_input_port


def selectOutputPort():
    portnrstr = input("Select the output port by typing the corresponding number: ")
    selected_output_port = int(portnrstr)

    return selected_output_port


def main(args=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    aadd = ap.add_argument
    aadd('-b', '--bpm', type=float, default=100,
         help="Beats per minute (BPM) (default: %(default)s)")
    aadd('--virtualout', type=bool, default=False,
         help="Create a MIDI out to SW instruments (like e.g. Korg opsix native) (default: %(default)s)")
    aadd('-r', '--repeats', type=int, default=0,
         help="Number of repeats. 0=infinite (default: %(default)s)")
    aadd('-c', '--channel', type=int, default=1, metavar='CH',
         help="MIDI channel (default: %(default)s)")
    aadd('-p', '--port',
         help="MIDI output port number (default: ask)")
    aadd('-k', '--kit', type=int, metavar='KIT',
         help="Drum kit MIDI program number (default: none)")
    aadd('--bank-msb', type=int, metavar='MSB',
         help="MIDI bank select MSB (CC#00) number (default: none)")
    aadd('--bank-lsb', type=int, metavar='MSB',
         help="MIDI bank select LSB (CC#32) number (default: none)")
    aadd('-H', '--humanize', type=float, default=0.0, metavar='VAL',
         help="Random velocity variation (float, default: 0, try ~0.03)")
    aadd('-m', '--midimap', type=argparse.FileType(), metavar='DMM',
         help="Midi Map File to map the drum instrument shortcuts to MIDI notes")
    aadd('pattern', nargs='?', type=argparse.FileType(),
         help="Drum pattern file (default: use built-in pattern)")

    args = ap.parse_args(args)

    if args.midimap:
        drummidimap = args.midimap.read()
    else:
        drummidimap = DRUMMIDIASSIGN_KorkWavestate_DrumKit

    if args.pattern:
        pattern = args.pattern.read()
    else:
        pattern = FUTUREDRUMPATTERN1

    kit = (args.bank_msb, args.bank_lsb, args.kit)
    drumpattern = dp.Drumpattern(pattern, drummidimap, kit=kit,
                          humanize=args.humanize)

    list_output_ports()



    if args.virtualout:
        midiout = rtmidi.MidiOut()
        midiout.open_virtual_port("MultiMidiSequencer")
    else:
        selected_output_port = selectOutputPort()
        midiout, port_name = open_midioutput(selected_output_port)


    seq = pseq.PatternSequencer(midiout, drumpattern, args.bpm, args.repeats, args.channel - 1)

    print("Playing drum loop at %.1f BPM, press Control-C to quit." % seq.bpm)

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print('')
    finally:
        seq.done = True  # And kill it.
        seq.join()
        midiout.close_port()
        del midiout
        print("Done")


if __name__ == "__main__":
    sys.exit(main() or 0)
