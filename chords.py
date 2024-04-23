from typing import List
from pretty_midi import Note
import random


def parse_transition_matrix(file: str) -> List[List[float]]:

    matrix = []

    with open(file, 'r') as f:
        for line in f.readlines():
            matrix.append([float(p) for p in line.split('\t')])

    return matrix


def generate_chords(matrix: List[List[float]], M: int) -> List[int]:
    """Generates chords in a Markovian process using the supplied transition matrix

    Args:
        matrix (List[List[float]]): transition matrix used
        M (int): number of chords to generate

    Returns:
        List[int]: sequence of numbers from 1-7, each representing the note of
        the scale on which the chord is build
    """

    output = [1]

    for _ in range(M):

        probabilities = matrix[output[-1] - 1]

        p = random.random()

        for chord, probability in enumerate(probabilities):
            
            p -= probability

            if p < 0:
                output.append(chord + 1)
                break

    return output


def chords_to_midi_pitches(
        chords: List[int],
        tonic_midi: int = 48,
        mood: str = 'major',
    ) -> List[Note]:
    """Converts a list of chords into a list of MIDI notes

    Args:
        chords (List[int]): list of chords, perhaps outputted by `generate_chords`
        tonic_midi (int, optional): the MIDI note to use as the tonic. Defaults to 48 (C3).
        mood (str, optional): mood of the chords ('major' or 'minor'). Defaults to 'major'.

    Returns:
        List[Note]: _description_
    """

    # key_moods[mood][chord] = (number of half steps above the tonic, chord mood)
    # i.e. key_moods['major'][3] = (major 3rd is 4 half steps, iii chord is minor)
    key_moods = {
        'major': [
            None,
            (0, 'major'),
            (2, 'minor'),
            (4, 'minor'),
            (5, 'major'),
            (7, 'major'),
            (9, 'minor'),
            (11, 'dim'),
        ],
        'minor': [
            None,
            (0, 'minor'),
            (2, 'dim'),
            (3, 'major'),
            (5, 'minor'),
            (7, 'major'),
            (8, 'major'),
            (10, 'major'),
        ]
    }

    # Number of half steps above the root for the middle and top notes of the chord,
    # respectively
    chord_offsets = {
        # 4: major 3rd, 7: perfect 5th
        'major': (4, 7),
        # 3: minor 3rd, 7: perfect 5th
        'minor': (3, 7),
        # 3: minor 3rd: 6: diminished 5th
        'dim': (3, 6),
        # 4: major 3rd: 8: augmented 5th
        'aug': (4, 8),
    }

    notes_list = []

    for chord in chords:

        # Figure out the offsets for the middle and top chords
        root_pitch, chord_mood = key_moods[mood][chord]
        middle_offset, top_offset = chord_offsets[chord_mood]

        # Generate the pitches for the three notes
        root = tonic_midi + root_pitch
        middle = tonic_midi + root_pitch + middle_offset
        top = tonic_midi + root_pitch + top_offset

        # And add them to the list
        notes_list.append([root, middle, top])

    return notes_list
