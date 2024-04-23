import random
import textwrap


def run_language():
    """Call `generate_mm_text` with the provided parameters."""

    # Run tidy text on both Heart of Darkness and Paradise Lost
    from tidy_text import tidy_text
    tidy_text('heart_of_darkness.txt')
    tidy_text('paradise_lost.txt')

    # Perform the Markov model for both texts
    for name in 'heart_of_darkness', 'paradise_lost':

        # Determine the file name based on which text we're reading
        file_name = f'tidy_{name}.txt'

        # Output length; 1000 per the problem set
        M = 1000

        # Generate order 1-4 markov models, saving them to their corresponding file
        for order in 1, 2, 3, 4:
            generated_text = generate_mm_text(file_name, order, M)

            # Dump the text to the file as specified by the problem set writeup
            output_file_name = f'{name}_mm_{order}.txt'
            with open(output_file_name, 'w') as output_file:
                print(f'Written to {output_file_name}')
                output_file.write(generated_text)


def generate_mm_text(file_name, order, M):
    """Create a Markov model for a given text file and output artificially
    generated text from the model.

    Args:
        file_name (str): path of the text to process
        order (int): order of the Markov model
        M (int): the length of the number of characters in the returned generated
        string

    Returns:
        A string of randomly generated text using a Markov model
    """
    # Read the contents of the file
    f = open(file_name, "r")

    if f is None:
        print("Can't open " + file_name)
    else:
        contents = f.read()
        f.close()
        contents = contents.replace("\n", "")
        contents = contents.replace("\r", "")

    # Collect the counts necessary to estimate transition probabilities
    # This dictionary will store all the data needed to estimate the Markov model:
    txt_dict = collect_counts(contents, order)

    # display_dict(txt_dict)

    # Generate artificial text from the trained model
    seed = contents[0:order]
    text = seed

    for _ in range(M):
        next_character = generate_next_character(seed, txt_dict)
        text += next_character
        seed = seed[1:] + next_character

    text_list = textwrap.wrap(text, 72)
    text = "\n".join(text_list)

    # Return the generated text
    return text


def display_dict(txt_dict):
    """Print the text dictionary as a table of keys to counts.
    Currently accepts a dictionary specified by the return documentation in the
    `build_dict` function.

    You will need to modify this function to accept the dictionary returned by
    the `collect_counts` function.

    Arguments:
        txt_dict (dict) - Mapping keys (as strings) to counts (as ints). After
        modification for `collect_counts`, the txt_dict will map keys (as strings)
        to dictionaries of counts and followers described in the return method
        of `collect_counts`.
    """
    print("key\tcount\tfollower counts")
    for key in txt_dict.keys():

        k_tuple_count = txt_dict[key]

        # Print the key
        print(key, end='\t')

        # Print the count
        print(k_tuple_count['count'], end='\t\t')

        # Print the follower counts
        for follower, count in k_tuple_count['followers'].items():
            print(f'{follower}:{count}', end=' ')

        # End the entry with a newline
        print()


def build_dict(contents, k):
    """Builds a dictionary of k-character (k-tuple) substring counts. Store the
    dictionary mapping from the k-tuple to an integer count.

    Args:
        contents (str): the string contents of to count
        k (int): number of characters in the substring

    Returns:
        a text dictionary mapping k-tuple to an integer
        Example return value with k=2:
        { 
            "ac": 1,
            "cg": 2,
            ... 
        }
    """
    counts = {}

    # In order to not consider the last complete k-tuple (which would be the interval
    # [l-k, l), where l is the length of contents), the last tuple we consider is l-k-1,
    # meaning we end iteration at l - k, since the end of a range is exclusive.
    for start_idx in range(len(contents) - k):
        k_tuple = contents[start_idx:start_idx+k]

        # Get the previous count, starting at 0 if this k-tuple is new
        count = counts.get(k_tuple, 0)

        # Increment the count
        count += 1

        # Store the count back in the dict
        counts[k_tuple] = count

    return counts


def collect_counts(contents, k):
    """Build a k-tuple dictionary mapping from k-tuple to a dictionary of
    of counts and dictionary of follower counts.
    
    Args:
        contents (str): the string contents of to count
        k (int): number of characters in the substring

    Returns:
        a dictionary mapping k-tuple to a dictionary of counts and dictionary
        of follower counts. Example return value with k=2:
        {
            "ac": {
                "count": 1,
                "followers": {"g": 1, "c": 2}
            },
            ...
        }

    Note: This function will similar to `build_dict`. We separated the 
    k-character and follower counting to explain each as distinct concepts. You
    should use the k-character counting code you wrote in `build_dict` as a 
    starting point.

    While the Markov model only needs to use `collect_counts` to generate text,
    our auto-grader will test the behavior of `build_dict` so that function 
    does need to work properly.
    """
    counts = {}

    # In order to not consider the last complete k-tuple (which would be the interval
    # [l-k, l), where l is the length of contents), the last tuple we consider is l-k-1,
    # meaning we end iteration at l - k, since the end of a range is exclusive.
    for start_idx in range(len(contents) - k):
        k_tuple = contents[start_idx:start_idx + k]
        follower = contents[start_idx + k]

        # Get the entry on this tuple. Since dictionaries are mutable (yucky), we can't
        # use the `get` function. We instead must use a try/except paradigm.
        try:
            k_tuple_count_dict = counts[k_tuple]
        except KeyError:
            k_tuple_count_dict = {
                'count': 0,
                'followers': {},
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


def generate_next_character(seed, txt_dict):
    """Randomly select the next character of a k-tuple using the follower
    counts to determine the probability.

    Args:
        seed (str): k-tuple to follow from
        txt_dict (dict): k-tuple count follower dictionary

    Returns:
        (str) of the next character
    """

    # Unpack the dictionary
    k_tuple_entry = txt_dict[seed]
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
            return follower


if __name__ == "__main__":
    """Main method call, do not modify"""
    run_language()

