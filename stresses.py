import pronouncing as p
from typing import List


def get_possible_stresses(stress_pattern: str) -> List[str]:
    """
    any subset of the target stress pattern.
    """
    possible_stresses = []
    for index in range(len(stress_pattern)):
        possible_stresses.append(stress_pattern[:index + 1])
    return possible_stresses

def get_possible_stresses_rev(stress_pattern: str) -> List[str]:
    """
    any subset of the target stress pattern.
    """
    possible_stresses = []
    for index in range(len(stress_pattern)):
        possible_stresses.append(stress_pattern[-index:])
    return possible_stresses


def word_matches_stress(word: str, stress_pattern_match: str) -> bool:
    '''
    eg: stress_pattern_match = "010"
    '''
    pronunciations = p.phones_for_word(
        word)  # word can have more than 1 pronunciation. eg: lead of a pencil, someone lead someone
    for pronunciation in pronunciations:
        original_stress_pattern = p.stresses(pronunciation)

        # we consider both 1 and 2 as a stressed syllable
        # our generated pattern match is only ever 1s and 0s
        stress_pattern = original_stress_pattern.replace("2", "1")

        # in case 1 pronunciation matches but the other one doesn't
        if stress_pattern == stress_pattern_match:
            return True

    return False

def word_fits_pattern(word: str, stress_pattern: str) -> bool:
    return any(word_matches_stress(word, stress) for stress in get_possible_stresses(stress_pattern))