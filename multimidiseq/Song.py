class Song(object):
    """a song is sub-structured into
    song parts. Each part can have several tracks."""
    def __init__(self, name):
        self.name = name
        self.tracks = []
        pass
