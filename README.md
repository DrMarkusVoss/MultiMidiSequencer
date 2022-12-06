# MultiMidiSequencer
A software sequencer that allows for multiple different sequences running at the same time using MIDI


## Example with a Korg Wavestate
Check out this repo on your PC (MAC).


Import the performance "./PresetsExtDevices/KorgWavestate/MV Simple Drumkit.wsperf" that is here in the repository into your Korg Wavestate using the
Wavestate Editor/Librarian Software and then switch to that performance.

On your PC (MAC), execute the following command:

```
 python3 multimidiseq.py -m ./DrumMidiMappings/Korg_Wavestate_Drm_WS_Drum_Kit.dmm ./DrumSeqPatterns/basic_drum_2.sdp 
```

The file `Korg_Wavestate_Drm_WS_Drum_Kit.dmm` contains the MIDI mapping to the Wavestate with the given performance.

The file `four_on_the_floor.sdp` contains the beat patterns that will be played.

## Example with the Singular Sound Beat Buddy Pedal
Connect the Beat Buddy MIDI-in to your Audio interfaces MIDI-out.

Then, on your PC (MAC), execute the following command:

```
 python3 multimidiseq.py -m ./DrumMidiMappings/BeatBuddy.dmm ./DrumSeqPatterns/basic_drum_2.sdp 
```

## Installation Requirements
- needs Python3 (tested with version 3.8.2; definitely a version >3.2 needed as argparse is used) and pip3 (usually comes with Python)
- install `python-rtmidi` by executing: `pip3 install python-rtmidi`

## Development Notes:
This code is 

based on: `drumseq.py` 

from here: https://github.com/SpotlightKid/python-rtmidi/tree/master/examples/drumseq

which is itself based on:

MIDI Drum sequencer prototype, by Michiel Overtoom, motoom@xs4all.nl (http://www.michielovertoom.com/).

The code will subsequently be reworked into the idea that I have in mind.

The ideas for the sequencers that will be implemented are influenced by "real world sequencers" (but are adopted to
my ideas) from:
- Korg Wavestate
- Behringer RD-9 (which itself is a clone of the Roland TR909)
- Korg Minilogue XD
- and several others that I saw being programmed in YouTube videos

Enjoy!

Dr. Markus Voss


