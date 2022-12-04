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
"""Play drum pattern from file to MIDI out."""

import argparse
import sys
import threading

from random import gauss
from time import sleep, time as timenow

from rtmidi.midiutil import open_midioutput, list_output_ports, list_input_ports
from rtmidi.midiconstants import (ALL_SOUND_OFF, BANK_SELECT_LSB,
                                  BANK_SELECT_MSB, CHANNEL_VOLUME,
                                  CONTROL_CHANGE, NOTE_ON, PROGRAM_CHANGE)


FUNKYDRUMMER = """
    #  1...|...|...|...
    36 x.x.......x..x.. Bassdrum
    38 ....x..m.m.mx..m Snare
    42 xxxxx.x.xxxxx.xx Closed Hi-hat
    46 .....x.x.....x.. Open Hi-hat
"""

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


DRUMPATTERN1 = """"
36 x.....s.x.......x.....m.x....... Bassdrum
53 xsssxsssxsssxsssxsssxsssxsssxsss Closed Hi-hat
"""


DRUMPATTERN2 = """"
# 36 x.....s.x.......x.....m.x....... Bassdrum
53 x+++x+++x+++x+++x+++x+++x+++x+++ Closed Hi-hat
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

class Sequencer(threading.Thread):
    """MIDI output and scheduling thread."""

    def __init__(self, midiout, pattern, bpm, channel=0, volume=127):
        super(Sequencer, self).__init__()
        self.midiout = midiout
        self.bpm = max(20, min(bpm, 400))
        self.interval = 15. / self.bpm
        self.pattern = pattern
        self.channel = channel
        self.volume = volume
        self.start()

    def run(self):
        self.done = False
        self.callcount = 0
        self.activate_drumkit(self.pattern.kit)
        cc = CONTROL_CHANGE | self.channel
        self.midiout.send_message([cc, CHANNEL_VOLUME, self.volume & 0x7F])

        # give MIDI instrument some time to activate drumkit
        sleep(0.3)
        self.started = timenow()

        while not self.done:
            self.worker()
            self.callcount += 1
            # Compensate for drift:
            # calculate the time when the worker should be called again.
            nexttime = self.started + self.callcount * self.interval
            timetowait = max(0, nexttime - timenow())
            if timetowait:
                sleep(timetowait)
            else:
                print("Oops!")

        self.midiout.send_message([cc, ALL_SOUND_OFF, 0])

    def worker(self):
        """Variable time worker function.

        i.e., output notes, emtpy queues, etc.

        """
        self.pattern.playstep(self.midiout, self.channel)

    def activate_drumkit(self, kit):
        if isinstance(kit, (list, tuple)):
            msb, lsb, pc = kit
        elif kit is not None:
            msb = lsb = None
            pc = kit

        cc = CONTROL_CHANGE | self.channel
        if msb is not None:
            self.midiout.send_message([cc, BANK_SELECT_MSB, msb & 0x7F])

        if lsb is not None:
            self.midiout.send_message([cc, BANK_SELECT_LSB, lsb & 0x7F])

        if kit is not None and pc is not None:
            self.midiout.send_message([PROGRAM_CHANGE | self.channel, pc & 0x7F])


class DrumpatternOrg(object):
    """Container and iterator for a multi-track step sequence."""

    velocities = {
        "-": None,  # continue note
        ".": 0,     # off
        "+": 10,    # ghost
        "s": 60,    # soft
        "m": 100,   # medium
        "x": 120,   # hard
    }

    def __init__(self, pattern, kit=0, humanize=0):
        self.instruments = []
        self.kit = kit
        self.humanize = humanize

        pattern = (line.strip() for line in pattern.splitlines())
        pattern = (line for line in pattern if line and line[0] != '#')

        for line in pattern:
            parts = line.split(" ", 2)
            print(parts)

            if len(parts) == 3:
                patch, strokes, description = parts
                patch = int(patch)
                self.instruments.append((patch, strokes))
                self.steps = len(strokes)

        self.step = 0
        self._notes = {}

    def reset(self):
        self.step = 0

    def playstep(self, midiout, channel=9):
        for note, strokes in self.instruments:
            char = strokes[self.step]
            velocity = self.velocities.get(char)

            if velocity is not None:
                if self._notes.get(note):
                    midiout.send_message([NOTE_ON | channel, note, 0])
                    self._notes[note] = 0
                if velocity > 0:
                    if self.humanize:
                        velocity += int(round(gauss(0, velocity * self.humanize)))

                    midiout.send_message([NOTE_ON | channel, note, max(1, velocity)])
                    print([NOTE_ON | channel, note, max(1, velocity)])
                    self._notes[note] = velocity

        self.step += 1

        if self.step >= self.steps:
           self.step = 0

class Drumpattern(object):
    """Container and iterator for a multi-track step sequence."""

    velocities = {
        "-": None,  # continue note
        ".": 0,     # off
        "+": 10,    # ghost
        "s": 60,    # soft
        "m": 100,   # medium
        "x": 120,   # hard
    }

    def __init__(self, pattern, drummidimapping, kit=0, humanize=0):
        self.instruments = []
        self.kit = kit
        self.humanize = humanize
        self.drummidimapping_raw = drummidimapping
        self.drummidimapping = {}

        self.initDrumMidiMapping()

        pattern = (line.strip() for line in pattern.splitlines())
        pattern = (line for line in pattern if line and line[0] != '#')

        for line in pattern:
            parts = line.split(" ", 2)
            print(parts)

            if len(parts) == 2:
                patch, strokes = parts
                patch = patch
                self.instruments.append((patch, strokes))
                self.steps = len(strokes)

        self.step = 0
        self._notes = {}

    def initDrumMidiMapping(self):
        dmm1 = (line.strip() for line in self.drummidimapping_raw.splitlines())
        dmm2 = (line for line in dmm1 if line and line[0] != '#')
        for line in dmm2:
            parts = line.split(" ", 2)
            self.drummidimapping[parts[0]] = int(parts[1])
        print(self.drummidimapping)


    def reset(self):
        self.step = 0

    def playstep(self, midiout, channel=9):
        for note, strokes in self.instruments:
            char = strokes[self.step]
            velocity = self.velocities.get(char)

            if velocity is not None:
                if self._notes.get(note):
                    midiout.send_message([NOTE_ON | channel, self.drummidimapping[note], 0])
                    self._notes[note] = 0
                if velocity > 0:
                    if self.humanize:
                        velocity += int(round(gauss(0, velocity * self.humanize)))

                    midiout.send_message([NOTE_ON | channel, self.drummidimapping[note], max(1, velocity)])
                    print([NOTE_ON | channel, note, self.drummidimapping[note], max(1, velocity)])
                    self._notes[note] = velocity

        self.step += 1

        if self.step >= self.steps:
           self.step = 0

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
        #pattern = DRUMPATTERN1
        kit = (args.bank_msb, args.bank_lsb, args.kit)
        pattern = Drumpattern(FUTUREDRUMPATTERN1, drummidimap, kit=kit,
                               humanize=args.humanize)

    kit = (args.bank_msb, args.bank_lsb, args.kit)
    drumpattern = Drumpattern(pattern, drummidimap, kit=kit,
                          humanize=args.humanize)




    list_output_ports()

    selected_output_port = selectOutputPort()

    midiout, port_name = open_midioutput(selected_output_port)

    seq = Sequencer(midiout, drumpattern, args.bpm, args.channel - 1)

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
