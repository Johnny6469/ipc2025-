import random

# Target phrase that the algorithm will try to reach.
TARGET = "METHINKS IT IS LIKE A WEASEL"

# Number of "children" generated per generation.
NUM_PHRASES = 100

# Mutation probability per character (between 0 and 1).
MUTATION_RATE = 0.05

# Generation counter (incremented in the main loop).
generation = 0

# Set of allowed characters in the phrases
# (uppercase letters A-Z and space).
ALPHABET = "".join(chr(i) for i in range(65, 91)) + " "


def random_phrase(length):
    """
    Generates and returns a random phrase of the given length.
    """
    # For each position, choose a random character from ALPHABET
    # and join everything together.
    return "".join(random.choice(ALPHABET) for _ in range(length))


def accuracy(candidate):
    """
    Calculates how many characters in 'candidate' match those in TARGET.
    """
    matches = 0  # Counter for position-by-position matches.

    # Iterate over pairs (c, t) of characters: one from candidate and
    # the corresponding one from TARGET, using 'zip' to iterate side by side.
    for c, t in zip(candidate, TARGET):
        if c == t:  # If there is a match in the same position, count 1.
            matches += 1

    return matches


def mutate(phrase, rate=0.05):
    """
    Applies random mutations to a phrase, character by character.
    """
    new_phrase = []  # Accumulates characters (mutated or preserved).

    # For each character 'c' in the original phrase:
    for c in phrase:
        # Generate a uniform random number in [0, 1).
        # If it is less than 'rate', mutate (replace with random character).
        if random.random() < rate:
            new_phrase.append(random.choice(ALPHABET))
        else:
            # Otherwise, keep the original character.
            new_phrase.append(c)

    # Join the list of characters into a string.
    return "".join(new_phrase)


def best_child(phrase, n=NUM_PHRASES):
    """
    Generates 'n' children from 'phrase' (via mutate)
    and returns the most accurate one.
    """
    # Create a list of 'n' mutated variations of the input phrase.
    children = [mutate(phrase, MUTATION_RATE) for _ in range(n)]

    # Select and return the child with the highest accuracy
    # (selection criterion).
    return max(children, key=accuracy)


# Read an initial phrase from the user. If empty (ENTER),
# generate a random one.
initial = input(
    "Enter the initial phrase (or press ENTER for a random one): "
)

if initial == "":
    # If the user does not provide a phrase, create one.
    initial = random_phrase(len(TARGET))
else:
    # Normalize the input
    initial = initial.upper().ljust(len(TARGET))[:len(TARGET)]

# Evolutionary loop: repeat until the current phrase is identical to TARGET.
while initial != TARGET:
    generation += 1  # Advance the generation counter.

    # Generate 'NUM_PHRASES' children from 'initial' and choose the best.
    initial = best_child(initial)

    # Display the best candidate of the current generation.
    print(f"Generation {generation}: {initial}")

# When the current phrase reaches TARGET, the loop ends and we
#  report the total.
print(f"Target reached in {generation} generations.")
