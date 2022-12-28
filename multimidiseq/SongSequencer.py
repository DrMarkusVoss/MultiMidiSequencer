import threading
from time import sleep, time as timenow
from rtmidi.midiconstants import (ALL_SOUND_OFF, BANK_SELECT_LSB,
                                  BANK_SELECT_MSB, CHANNEL_VOLUME,
                                  CONTROL_CHANGE, NOTE_ON, PROGRAM_CHANGE)
from multimidiseq import Track as tk

class SongSequencer(threading.Thread):
    """MIDI output and scheduling thread."""

    def __init__(self, midiout, track_raw, repeats=1, channel=0, volume=127):
        super(SongSequencer, self).__init__()

        self.track = tk.Track(track_raw)

        self.midiout = midiout
        self.bpm = max(20, min(self.track.bpm, 400))
        self.interval = 15. / self.bpm
        self.repeats=1
        self.channel = channel
        self.volume = volume
        print(self.track)
        self.start()
        self.current_pattern = None
        self.current_pattern_name = ""
        self.pattern_length_sum = 0

    def run(self):
        self.done = False
        self.callcount = 0
        cc = CONTROL_CHANGE | self.channel
        self.midiout.send_message([cc, CHANNEL_VOLUME, self.volume & 0x7F])

        # give MIDI instrument some time to activate drumkit
        sleep(0.3)
        self.started = timenow()
        ind = 0
        self.current_pattern = self.track.patterns[self.track.trackseq[ind]]
        self.current_pattern_name = self.track.trackseq[ind]
        print("now playing pattern: " + self.current_pattern_name)

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


            if self.callcount == self.pattern_length_sum + self.current_pattern.length:
                ind += 1
                if len(self.track.trackseq) > ind:
                    self.pattern_length_sum += self.current_pattern.length
                    self.current_pattern = self.track.patterns[self.track.trackseq[ind]]
                    self.current_pattern_name = self.track.trackseq[ind]
                    print("now playing pattern: " + self.current_pattern_name)
                else:
                    self.done = True

        self.midiout.send_message([cc, ALL_SOUND_OFF, 0])
        print("finished!")

    def worker(self):
        """Variable time worker function.

        i.e., output notes, emtpy queues, etc.

        """
        # TODO: work through the tracks list of patterns to be played,
        #       there step through each pattern step-by-step
        self.current_pattern.playstep(self.midiout, self.channel)



