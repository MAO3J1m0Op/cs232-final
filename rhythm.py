from typing import List, Tuple
from pretty_midi import Note
import random


def midi_to_list(midi_notes: List[Note], beats: List[float]) -> Tuple[List[str], List[int]]:
    """Converts a list of MIDI notes into a list of MIDI pitches and a rhythm list

    Args:
        midi_notes (List[Note]): the list of notes to convert
        beats (List[float]): list of beats used to interpret the rhythm

    Returns:
        Tuple[List[str], List[int]]: list of rhythms, and list of MIDI pitches
    """

    next_beat = 1

    notes = sorted(midi_notes, key=lambda n: n.start)
    parsed_notes = []
    parsed_pitches = []

    for n in range(1, len(notes)):

        # Get the start time of two consecutive notes
        prev_note_start = notes[n-1].start
        current_note_start = notes[n].start

        # Parse out the pitch
        pitch = notes[n-1].pitch
        parsed_pitches.append(pitch)

        # Find the duration
        note_dur = notes[n-1].end - notes[n-1].start

        # Find the time between the two notes
        note_gap = current_note_start - prev_note_start

        # Ensures that the next beat is always the one right after the start of this note
        while prev_note_start > beats[next_beat]:
            next_beat += 1

        # Gets the length of the beat in MIDI time units
        beat_length = beats[next_beat] - beats[next_beat - 1]

        # # Gets the length of the note in comparison to the length of the beat
        gap_beats = note_gap / beat_length
        dur_beats = note_dur / beat_length

        start_subd = get_best_subdivision(prev_note_start, 8)
        gap_subd = get_best_subdivision(gap_beats, 8)
        beats_subd = get_best_subdivision(dur_beats, 8)

        parsed_notes += fill_gap(gap_subd, beats_subd)

    parsed_notes = [n for n in parsed_notes if n != 'whole_rest']

    return parsed_notes, parsed_pitches


def get_best_subdivision(num: float, num_subdivisions: int) -> int:
    """Returns an integer, n, such that n / num_subdivisions is closest to the
    provided number.

    Args:
        num (float)
        num_subdivisions (int)

    Returns:
        int
    """
    cycles = 0
    while True:
        for subdiv in range(num_subdivisions):
            left_bound = (2*subdiv - 1) / (2*num_subdivisions)
            right_bound = (2*subdiv + 1) / (2*num_subdivisions)
            if left_bound <= num <= right_bound:
                return subdiv + (cycles * num_subdivisions)
        cycles += 1
        num -= 1


def choose_note(note_length: int, subdiv_names: List[Tuple[str, int]]) -> Tuple[str, int]:
    """Choses the best note out of the list of notes provided

    Args:
        note_length (int): the length of the note, in subdivisions
        subdiv_names (List[Tuple[str, int]]): a list of notes pairing their name
        and their length

    Returns:
        Tuple[str, int]: the name and length of the chosen note, or (None, 0) if
        no note was able to be chosen.
    """
    for name, subdiv in subdiv_names:
        if note_length >= subdiv:
            return name, subdiv
        
    return None, 0


def fill_gap(gap_length: int, note_length: int) -> List[str]:
    """Fills a gap containing a MIDI note with notes

    Args:
        gap_length (int): the length, in subdivisions, of the distance between
        this MIDI note and the next 
        note_length (int): the duration of this MIDI note in subdivisions

    Returns:
        List[str]: a list of notes that completely fills this gap
    """

    notes = []

    rest_length = gap_length - note_length

    names_and_subdivs = [
        ('whole',        32),
        ('half',         16),
        ('quarter',       8),
        ('eighth',        4),
        ('sixteenth',     2),
        ('thirty-second', 1)
    ]

    # Get the first note
    first_note_name, first_note_subdiv = choose_note(note_length, names_and_subdivs)
    if first_note_name is not None:
        notes.append(first_note_name + '_note')
        note_length -= first_note_subdiv

    # Add the remainder of the note tied together
    while True:
        name, subdiv = choose_note(note_length, names_and_subdivs)
        if name is None:
            break

        notes.append(name + '_tie')
        note_length -= subdiv

    # Add the rest
    while True:
        name, subdiv = choose_note(rest_length, names_and_subdivs)
        if name is None:
            break

        notes.append(name + '_rest')
        rest_length -= subdiv

    return notes


def collect_counts(contents: list, k):
    counts = {}

    # In order to not consider the last complete k-tuple (which would be the interval
    # [l-k, l), where l is the length of contents), the last tuple we consider is l-k-1,
    # meaning we end iteration at l - k, since the end of a range is exclusive.
    for start_idx in range(len(contents) - k):
        k_tuple = tuple(contents[start_idx:start_idx + k])
        follower = contents[start_idx + k]

        # Get the entry on this tuple. Since dictionaries are mutable (yucky), we can't
        # use the `get` function. We instead must use a try/except paradigm.
        try:
            k_tuple_count_dict = counts[k_tuple]
        except KeyError:
            k_tuple_count_dict = {
                'count': 0,
                'followers': dict(),
            }

        # Increment the k-tuple's count
        k_tuple_count_dict['count'] += 1

        # Increment the tuple follower's count
        follower_count = k_tuple_count_dict['followers'].get(follower, 0)
        k_tuple_count_dict['followers'][follower] = follower_count + 1

        # Store the count back in the dict. Necessary since k_tuple_count_dict
        # might be a new dictionary. I'm not a big fan of Python's auto-referencing
        # at all.
        counts[k_tuple] = k_tuple_count_dict

    return counts
     

def generate_rhythm(M: int, k: int, seed: List[str]) -> List[str]:
    """Generates a rhythm designed to continue that which is passed as a seed

    Args:
        M (int): the number of elements in the continuation
        k (int): order of the Markov chain used to generate the rhythm
        seed (List[str]): element on which the Markov model is trained

    Returns:
        List[str]: generated text, which will be of length M
    """
    
    counts = collect_counts(seed, k)

    # Generate artificial text from the trained model
    text = seed[0:k]
    seed = tuple(text)

    for _ in range(M):

        # Unpack the dictionary
        k_tuple_entry = counts[seed]
        total_counts = k_tuple_entry['count']
        counts_dict = k_tuple_entry['followers']

        # Generate a random number guaranteed to correspond with one of the followers
        # The counts dict can be thought of as a compressed array (think the first column
        # of the Burrows-Wheeler Matrix), and this number is an index into that array
        number = random.randint(0, total_counts - 1)

        # Find the count with which it's associated
        for follower, follower_count in counts_dict.items():

            # Subtract the counts from our index
            number -= follower_count

            # If number is now negative, that means that the index was within the bounds
            # of the "array" corresponding to this follower, so let's return this follower.
            if number < 0:
                text.append(follower)
                break

        seed = tuple(text[-k:])

    return text
