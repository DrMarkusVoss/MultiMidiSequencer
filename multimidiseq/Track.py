class Track(object):
    """a track is a sequence of patterns in a defined tempo."""
    def __init__(self, track_raw):
        self.name = "track1"
        self.bpm = 100.0
        self.patterns_shortcuts = {}
        self.trackseq = []
        self.initTrack(track_raw)


    def initTrack(self, track_raw):
        tr1 = (line.strip() for line in track_raw.splitlines())
        tr2 = (line for line in tr1 if line and line[0] != '#')

        for line in tr2:
            parts = line.split(" ")

            if len(parts) == 2:
                if parts[0] == "BPM":
                    self.bpm = float(parts[1])
                else:
                    self.patterns_shortcuts[parts[0]] = parts[1]
            if len(parts) > 2:
                self.name = parts[0]
                print(parts)
                for e in parts[1:len(parts)]:
                    self.trackseq.append(e)