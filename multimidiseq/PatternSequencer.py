import threading
from time import sleep, time as timenow
from rtmidi.midiconstants import (ALL_SOUND_OFF, BANK_SELECT_LSB,
                                  BANK_SELECT_MSB, CHANNEL_VOLUME,
                                  CONTROL_CHANGE, NOTE_ON, PROGRAM_CHANGE)


class PatternSequencer(threading.Thread):
    """MIDI output and scheduling thread."""

    def __init__(self, midiout, pattern, bpm, repeats=0, channel=0, volume=127):
        super(PatternSequencer, self).__init__()
        self.midiout = midiout
        self.bpm = max(20, min(bpm, 400))
        self.interval = 15. / self.bpm
        self.pattern = pattern
        self.repeats=repeats
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

            if not self.repeats==0:
                if self.callcount == self.repeats*self.pattern.length:
                    self.done = True

        self.midiout.send_message([cc, ALL_SOUND_OFF, 0])
        print("finished!")

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

