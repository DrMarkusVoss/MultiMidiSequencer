from random import gauss
from rtmidi.midiconstants import (ALL_SOUND_OFF, BANK_SELECT_LSB,
                                  BANK_SELECT_MSB, CHANNEL_VOLUME,
                                  CONTROL_CHANGE, NOTE_ON, PROGRAM_CHANGE)
class MultilineNotePattern(object):
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
        self.drummidimapping = {}
        self.steps = []
        self.step = []
        self._notes = {}
        self.voice_names = []
        # key = voice name, value = notes
        self.voices_notes = {}

        self.initMultilineNotePattern(pattern)
        print(self.voices_notes)
        print(self.instruments)

        #self.length = max(self.steps)

    def initMultilineNotePattern(self, pattern_raw):
        p1 = (line.strip() for line in pattern_raw.splitlines())
        p2 = (line for line in p1 if line and line[0] != '#')

        for line in p2:
            parts = line.split(" ")
            # print(parts)

            if len(parts) == 2:
                if parts[0] == "BPM":
                    self.bpm = float(parts[1])
                elif parts[0] == "DMM":
                    self.dmm_fn = parts[1]
                else:
                    self.pattern_shortcuts[parts[0]] = parts[1]

            if len(parts) > 2:
                voice_name = ""
                voice_name = parts[0]
                self.voice_names.append(voice_name)
                notelist = []
                notes = []
                vels = []

                for e in parts[1:len(parts)]:
                    if e not in ["", " "]:
                        if len(e) == 3:
                            vel = e[0]
                            vels.append(vel)
                            note = e[1:3]
                            notes.append(note)
                            vn_pair = [vel, note]
                            notelist.append(vn_pair)
                        else:
                            print("ERROR: Wrong note format: " + e)
                self.steps.append(len(notelist))
                self.instruments.append((voice_name, vels, notes))
                self.step.append(0)
                self.voices_notes[voice_name] = notelist

                # patch, strokes = parts
                # patch = patch
                # self.instruments.append((patch, strokes))
                #self.steps.append(len(strokes))
                # self.step.append(0)


    def reset(self):
        for i in enumerate(self.step):
            self.step[i] = 0


    def playstep(self, midiout, channel=9):
        # TODO: needs rework for the multilne note playing
        i=0
        for voice_name, strokes, notes in self.instruments:
            char = strokes[self.step[i]]
            velocity = self.velocities.get(char)
            note = notes[self.step[i]]

            if velocity is not None:
                if self._notes.get(notes[i]):
                    print(note, velocity)
                    midiout.send_message([NOTE_ON | channel, int(note), 0])
                    self._notes[notes[i]] = 0
                if velocity > 0:
                    if self.humanize:
                        velocity += int(round(gauss(0, velocity * self.humanize)))
                    print([NOTE_ON | channel, voice_name, note, max(1, velocity)])
                    midiout.send_message([NOTE_ON | channel, int(note), max(1, velocity)])

                    self._notes[notes[i]] = velocity

            self.step[i] += 1

            if self.step[i] >= self.steps[i]:
                self.step[i] = 0

            i += 1