from typing import List
from pydub import AudioSegment
from pydub.generators import Sine
from pretty_midi import Note

def get_frequency(midi_note: int):

    frequencies = [
        16.352, # C
        17.324, # C#
        18.354, # D
        19.445, # D#
        20.602, # E
        21.827, # F
        23.125, # F#
        24.500, # G
        25.957, # G#
        27.500, # A
        29.135, # A#
        30.868, # B
    ]

    octave = (midi_note // 12) - 1
    pitch = midi_note % 12

    return frequencies[pitch] * (2 ** octave)


def make_wav(
        tempo: int,
        file_name: str,
        rhythm: List[str],
        pitches: List[int],
        transpose: int = 0
    ):

    pitch_idx = 0

    wav = AudioSegment.silent(duration=0)

    # Get the tempo in terms of subdivisions per millisecond
    tempo_ms_subdivs = (60 * 1000) / (8 * tempo)

    for note in rhythm:
        duration_name, kind = note.split('_')

        match duration_name:
            case 'whole': duration_subdivs = 32
            case 'half': duration_subdivs = 16
            case 'quarter': duration_subdivs = 8
            case 'eighth': duration_subdivs = 4
            case 'sixteenth': duration_subdivs = 2
            case 'thirty-second': duration_subdivs = 1
            case x: raise ValueError(f'unknown note {x}')


        duration_ms = tempo_ms_subdivs * duration_subdivs

        if kind == 'rest':
            segment = AudioSegment.silent(duration=duration_ms)
        elif kind in ('tie', 'note'):

            segment = Sine(
                get_frequency(pitches[pitch_idx] + transpose)
            ).to_audio_segment(duration=duration_ms)
            
            if kind == 'note':
                pitch_idx += 1

        else:
            raise ValueError('invalid note type')

        wav += segment

    wav.export(file_name, format="wav")


def make_midi_note_list(
        tempo: int,
        rhythm: List[str],
        pitches: List[int | List[int]]
    ) -> List[Note]:

    tempo_s_subdivs = 60 / (8 * tempo)

    notes_list = []

    start = 0.0
    pitch_count = 0

    for note in rhythm:
        duration_name, kind = note.split('_')

        match duration_name:
            case 'whole': duration_subdivs = 32
            case 'half': duration_subdivs = 16
            case 'quarter': duration_subdivs = 8
            case 'eighth': duration_subdivs = 4
            case 'sixteenth': duration_subdivs = 2
            case 'thirty-second': duration_subdivs = 1
            case x: raise ValueError(f'unknown note {x}')

        duration_s = tempo_s_subdivs * duration_subdivs

        # Continue to write to the previous note
        if kind == 'tie':

            if notes_list:
                notes_list[-1].end += duration_s

        elif kind in ('rest', 'note'):

            # Create a new note
            if kind == 'note':
                    
                pitches_here = pitches[pitch_count]

                # If only one pitch is supplied, convert that one pitch into a list
                if type(pitches_here) is int:
                    pitches_here = [pitches_here]

                for pitch in pitches_here:
                    notes_list.append(
                        Note(velocity=60, pitch=pitch, start=start, end=start+duration_s)
                    )

                # Move to the next list of pitches
                pitch_count += 1

        else:
            raise ValueError('invalid note type')

        # Update the note start positions
        start += duration_s

    return notes_list
