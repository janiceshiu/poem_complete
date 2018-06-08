import pronouncing as p
from typing import List
import random
import re


def make_one_zero_str(length: int, start_stress: int) -> str:
    one_zero_str = ""
    for index in range(start_stress, length + start_stress):
        one_zero_str += str(index % 2)

    return one_zero_str


def get_possible_stresses(current_stresses: str) -> List[str]:
    """
    can assume that current_stresses is 0[1,2] repeated
    eg: current_stresses = "010"
    """
    iamb_pent_syllables = 10

    syllables = len(current_stresses)
    remaining_stresses = iamb_pent_syllables - syllables
    start_stress = remaining_stresses % 2  # if even, start with 0
    possible_stress_lengths = list(range(1, remaining_stresses + 1))
    return list(map(lambda length: make_one_zero_str(length, start_stress), possible_stress_lengths))


def guess_syllables(word: str) -> int:
    """
    how many successive groups of vowels are there? if none, assume it's no syllables
    """
    match = re.findall(r"[aeiou]+", word)
    return len(match)


def get_stress_for_word(word: str) -> str:
    pronunciations = p.phones_for_word(word)
    if not pronunciations:
        num_syllables = guess_syllables(word)
        return "?" * num_syllables
    else:
        return p.stresses(pronunciations[0])


def word_matches_stress(word: str, stress_pattern_match: str) -> bool:
    '''
    eg: stress_pattern_match = "010"
    '''
    # word can have more than 1 pronunciation. eg: lead of a pencil, someone
    # lead someone
    pronunciations = p.phones_for_word(word)

    for pronunciation in pronunciations:
        original_stress_pattern = p.stresses(pronunciation)

        # we consider both 1 and 2 as a stressed syllable
        # our generated pattern match is only ever 1s and 0s
        stress_pattern = original_stress_pattern.replace("2", "1")

        # in case 1 pronunciation matches but the other one doesn't
        if stress_pattern == stress_pattern_match:
            return True

    return False
