from random import gauss
from rtmidi.midiconstants import (ALL_SOUND_OFF, BANK_SELECT_LSB,
                                  BANK_SELECT_MSB, CHANNEL_VOLUME,
                                  CONTROL_CHANGE, NOTE_ON, PROGRAM_CHANGE)
class ChordPattern(object):
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
        self.steps = []
        self.step = []
        self._notes = {}

        self.initChordPattern(pattern)

        self.length = max(self.steps)



    def initChordPattern(self, pattern_raw):
        dp1 = (line.strip() for line in pattern_raw.splitlines())
        dp2 = (line for line in dp1 if line and line[0] != '#')

        for line in dp2:
            parts = line.split(" ", 2)
            # print(parts)

            if len(parts) == 2:
                patch, strokes = parts
                patch = patch
                self.instruments.append((patch, strokes))
                self.steps.append(len(strokes))
                self.step.append(0)


    def reset(self):
        for i in enumerate(self.step):
            self.step[i] = 0


    def playstep(self, midiout, channel=9):
        i=0
        for note, strokes in self.instruments:
            char = strokes[self.step[i]]
            velocity = self.velocities.get(char)

            if velocity is not None:
                if self._notes.get(note):
                    if note in self.drummidimapping.keys():
                        midiout.send_message([NOTE_ON | channel, self.drummidimapping[note], 0])
                    self._notes[note] = 0
                if velocity > 0:
                    if self.humanize:
                        velocity += int(round(gauss(0, velocity * self.humanize)))

                    if note in self.drummidimapping.keys():
                        midiout.send_message([NOTE_ON | channel, self.drummidimapping[note], max(1, velocity)])
                        print([NOTE_ON | channel, note, self.drummidimapping[note], max(1, velocity)])
                    else:
                        print("WARNING: Note for instrument " + note + " not played!")
                    self._notes[note] = velocity

            self.step[i] += 1

            if self.step[i] >= self.steps[i]:
                self.step[i] = 0

            i += 1