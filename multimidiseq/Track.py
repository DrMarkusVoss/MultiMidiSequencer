from multimidiseq import DrumPattern as dp

class Track(object):
    """a track is a sequence of patterns in a defined tempo."""
    def __init__(self, track_raw):
        self.name = "track1"
        self.bpm = 100.0
        # drum midi mapping
        self.dmm = None
        # filename to specified drum midi mapping
        self.dmm_fn = ""
        self.pattern_shortcuts = {}
        self.patterns = {}
        self.trackseq = []
        self.initTrack(track_raw)

    def initPatterns(self):
        if not dmm == None:
            for e in self.pattern_shortcuts:
                # open the pattern file
                file = open(self.pattern_shortcuts[e], mode='r')
                # read all lines at once
                pattern_raw = file.read()
                # close the file
                file.close()

                self.patterns[e] = dp.DrumPattern(pattern_raw, self.dmm)
        else:
            print("error: no midi mapping specified in track: " + self.name)



    def initTrack(self, track_raw):
        tr1 = (line.strip() for line in track_raw.splitlines())
        tr2 = (line for line in tr1 if line and line[0] != '#')

        for line in tr2:
            parts = line.split(" ")

            if len(parts) == 2:
                if parts[0] == "BPM":
                    self.bpm = float(parts[1])
                elif parts[0] == "DMM":
                    self.dmm = parts[1]
                else:
                    self.pattern_shortcuts[parts[0]] = parts[1]
            if len(parts) > 2:
                self.name = parts[0]
                print(parts)
                for e in parts[1:len(parts)]:
                    self.trackseq.append(e)