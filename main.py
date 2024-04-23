from typing import List
from pretty_midi import PrettyMIDI, Instrument

from chords import parse_transition_matrix, chords_to_midi_pitches, generate_chords
from rhythm import midi_to_list, generate_rhythm
from filegen import make_midi_note_list, make_wav


def main():

    # Change this as you please. Be warned: there are many undocumented bugs :)

    chords_with_rhythms('rhythmed_chords.mid', tonic=48, mood='major')
    # parse_take_five_sax()


def parse_take_five_sax():
    midi = PrettyMIDI('take5.mid')

    sax = midi.instruments[5]

    notes, pitches = midi_to_list(sax.notes, midi.get_beats())

    print(notes)
    print(pitches)

    make_wav(tempo=180, file_name='take5.wav', rhythm=notes, pitches=pitches)


def chords_with_rhythms(out_file: str, tonic: int, mood: str):
    midi = PrettyMIDI('simple_drum_beats.mid')

    instrument = midi.instruments[0]

    pitched_notes = []

    for i in range(100):
        pitched_notes.append([n for n in instrument.notes if n.pitch == i])

    print([(i, len(p)) for i, p in enumerate(pitched_notes)])

    beats = midi.get_beats()

    parsed_notes35, _ = midi_to_list(pitched_notes[35], beats)
    parsed_notes38, _ = midi_to_list(pitched_notes[38], beats)
    parsed_notes42, _ = midi_to_list(pitched_notes[42], beats)

    rhythm_aggregate = parsed_notes35 + parsed_notes38 + parsed_notes42

    markoved_rhythm = generate_rhythm(300, 2, rhythm_aggregate)

    matrix = parse_transition_matrix(f'{mood}.txt')
    markoved_chords = chords_to_midi_pitches(generate_chords(matrix, 1000), tonic_midi=tonic, mood=mood)

    notes = make_midi_note_list(tempo=120, rhythm=markoved_rhythm, pitches=markoved_chords)

    out = PrettyMIDI()
    
    chords = Instrument(program=0, is_drum=False, name='Chords')
    chords.notes = notes

    out.instruments = [chords]

    out.write(out_file)


def i_cant_quote_nick():
    chords_and_rhythms_separate('take5.mid', [40], '3yo_spectrum.mid', tonic=51, mood='minor')


def reasonable_chords_and_rhythms(tonic: int, mood: str):
    chords_and_rhythms_separate('simple_drum_beats.mid', [35, 38, 42], 'drums.mid', tonic, mood)


def chords_and_rhythms_separate(in_file: str, drum_pitches: List[int], out_file: str, tonic: int, mood: str):
    midi = PrettyMIDI(in_file)

    instrument = midi.instruments[0]

    pitched_notes = []

    for i in range(100):
        pitched_notes.append([n for n in instrument.notes if n.pitch == i])

    print([(i, len(p)) for i, p in enumerate(pitched_notes)])

    beats = midi.get_beats()

    notes = []

    for p in drum_pitches:
        parsed_notes, _ = midi_to_list(pitched_notes[p], beats)
        markoved = generate_rhythm(300, 3, parsed_notes)
        notes += make_midi_note_list(tempo=120, rhythm=markoved, 
                                 pitches=[p for _ in range(10000)])

    out = PrettyMIDI()
    drums = Instrument(program=42, is_drum=True, name='Drums')
    drums.notes = notes

    matrix = parse_transition_matrix(f'{mood}.txt')
    markoved_chords = generate_chords(matrix, M=100)

    pitches = chords_to_midi_pitches(markoved_chords, tonic_midi=48, mood=mood)

    chords = Instrument(program=0, is_drum=False, name='Chords')
    chords.notes = make_midi_note_list(tempo=120, rhythm=['whole_note' for _ in range(99)], pitches=pitches)

    out.instruments = [drums, chords]

    out.write(out_file)


if __name__ == '__main__':
    main()

