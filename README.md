# MultiMidiSequencer
A software sequencer that allows for multiple different sequences running at the same time using MIDI

## The Drum Pattern Sequencer
The drum pattern sequencer plays patterns encoded in ascii-based text files. It is inspired by the programming
principles of famous drum machines like the Roland TR808 and TR909 and it's clones, the Behringer RD-8 and RD-9.

A pattern is encoded according to the following rules in a text file:
- a "sequencer drum pattern" is stored in a file with the ending `.sdp`
- a line starting with a `#` is a comment and ignored for the pattern playing
- an empty line is ignored
- a "track line" represents an "instrument" with a dedicated pattern to be played
  - a track line starts with the instrument shortcut (e.g. `BD1` for bass drum 1) and is followed by a space
  - the instrument shortcuts are defined in a Drum MIDI Mapping file (`.dmm`, see folder `DrumMidiMappings`) and
    is an alias for a MIDI Note value
  - the second part after the instrument is the pattern that the instrument shall play encoded with characters,
    with each character representing a 1/16 note of a 4/4 beat.
  - tracks can have different length; the tracks that are shorter than others in the same file will be repeated as often
    as it matches the length of the longest track; to indicate that really nothing shall be played you have to 
    actively encode that with `.` (off) characters for the length of the longest track.
  - here is the character encoding:

```
Drum Pattern Characters:
        - : continue note   Send no note
        . : off             Note off
        + : ghost note      Note on with velocity 10
        s : soft            Note on with velocity 60
        m : medium          Note on with velocity 100
        x : hard            Note on with velocity 120
```

Here is a drum pattern example:

```
file: ./DrumSeqPatterns/basic_drum_2.sdp

# Sequencer Drum Pattern
# Basic Drum Pattern 2
# by Dr. Markus Voss

BD1 x.....s.x.......x.........x.....
SN1 ....m-......m-......m-......m-..
CHH xsss
CR1 x-..............................
```
This example is a pattern of 2 bars in a 4/4 beat described with 32 1/16 notes. `BD1` is the pattern for the
base drum (kick drum), `SN1` is for the snare drum, `CHH` is for the closed hi-hat and `CR1` is the crash cymbal.
Note that here the pattern for the closed hi-hat has only 4 characters, representing 4 1/16 notes. This means that 
during the whole two bars this pattern is repeated 8 times, matching the length of 32 notes for the whole pattern which
is defined by the longest track (which are basically all the others that are all 32 notes long). Principally, you
can have as many tracks in a file as you want. 

See examples of further drum patterns in the folder `DrumSeqPatterns` of this repository.

## Example with a Korg Wavestate
Check out this repo on your PC (MAC).


Import the performance `./PresetsExtDevices/KorgWavestate/MV Simple Drumkit.wsperf` that is here in the repository into your Korg Wavestate using the
Wavestate Editor/Librarian Software and then switch to that performance.

On your PC (MAC), execute the following command:

```
 python3 multimidiseq.py -m ./DrumMidiMappings/Korg_Wavestate_Drm_WS_Drum_Kit.dmm ./DrumSeqPatterns/basic_drum_2.sdp 
```

The file `Korg_Wavestate_Drm_WS_Drum_Kit.dmm` contains the MIDI mapping to the Wavestate with the given performance.

The file `basic_drum_2.sdp` contains the beat patterns that will be played.

## Example with the Singular Sound Beat Buddy Pedal
Connect the Beat Buddy MIDI-in to your Audio interfaces MIDI-out.

Then, on your PC (MAC), execute the following command:

```
 python3 multimidiseq.py -m ./DrumMidiMappings/BeatBuddy.dmm ./DrumSeqPatterns/basic_drum_2.sdp -b 80
```

This makes the Beat Buddy play the drum pattern defined in the file `./DrumSeqPatterns/basic_drum_2.sdp` at a tempo of 80 bpm.

## Installation Requirements
- needs Python3 (tested with version 3.8.2; definitely a version >3.2 needed as argparse is used) and pip3 (usually comes with Python)
- install `python-rtmidi` by executing: `pip3 install python-rtmidi`

## Development Notes
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
- Roland J-6
- and several others that I saw being programmed in YouTube videos

Enjoy!

Dr. Markus Voss


