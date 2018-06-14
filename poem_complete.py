#!.env/bin/python3

import nltk
from typing import List, Dict
from nltk.corpus import gutenberg
from collections import defaultdict
from word import Word
from stresses import get_possible_stresses, word_matches_stress, word_fits_pattern, get_possible_stresses_rev
import random
import pronouncing as p
import time
import pickle
import json
import re
from subprocess import call

# random.seed(1)

NGRAM_DICT = Dict[str, List[str]]
Line = str
Stanza = List[Line]
IAMBIC_PENTAMETER = "0101010101"

def load_or_create_ngram(reverse: bool = False) -> NGRAM_DICT:
    try:
        if reverse:
            with open('ngram_reverse_dict.json') as fp:
                ngram_dict = json.load(fp)
                return ngram_dict
        else:
            with open('ngram_dict.json') as fp:
                ngram_dict = json.load(fp)
                return ngram_dict

    except FileNotFoundError:
        words = gutenberg.words()
        filtered = list(filter(lambda word: word.isalpha(), words))
        filtered_lower = [word.lower() for word in filtered]

        ngram_dict = defaultdict(list)

        if reverse:
            ngrams = zip(filtered_lower[1:], filtered_lower)
        else:
            ngrams = zip(filtered_lower, filtered_lower[1:])
        for w1, w2 in ngrams:
            ngram_dict[w1].append(w2)

        if reverse:
            with open('ngram_reverse_dict.json', 'w') as fp:
                json.dump(ngram_dict, fp)
        else:
            with open('ngram_dict.json', 'w') as fp:
                json.dump(ngram_dict, fp)

        return ngram_dict


def convert_to_word(token: str) -> Word:
    pronunciations = p.phones_for_word(token)
    stress_patterns = [p.stresses(pronunciation).replace("2", "1")
                       for pronunciation in pronunciations]
    if stress_patterns:
        # pick one arbitrarily
        return Word(token, stress_patterns[0])
    else:
        number_syllables_guess = len(re.findall(r"[aeiou]+", token))
        return Word(token, "?" * number_syllables_guess)


def main():
    # start = input("How should we start your poem? ").lower().strip()

    start_sonnet = "Shall I".lower().strip()

    start_limerick = "There".lower().strip()

    words = [convert_to_word(token) for token in nltk.tokenize.word_tokenize(start_sonnet)]


    # print(list(map(len, get_possible_stresses(IAMBIC_PENTAMETER))))
    # print(words)

    ngram_dict = load_or_create_ngram()
    ngram_reverse_dict = load_or_create_ngram(reverse=True)

    sonnet = produce_sonnet(words, IAMBIC_PENTAMETER, ngram_dict, ngram_reverse_dict)
    for stanza in sonnet:
        for line in stanza:
            print(line.capitalize())
            say(line)

        print("")

    # for line in produce_limerick(words, ngram_dict, ngram_reverse_dict):
    #     print(line)
    #     say(line)



def say(line:str):
    call(["say", line])



def line_to_string(line:List[Word]) -> Line:
    return " ".join(word.spelling for word in line)


def produce_sonnet(start:List[Word], stress_pattern:str, ngram_dict:NGRAM_DICT, ngram_reverse_dict:NGRAM_DICT) -> List[Stanza]:

    qt1 = produce_quatrain(start, IAMBIC_PENTAMETER, ngram_dict, ngram_reverse_dict)

    # print(qt1)

    last_word = qt1[-1][-1]
    possible_words = get_possible_words(last_word, IAMBIC_PENTAMETER, ngram_dict)
    next_word = possible_words[0]
    qt2 = produce_quatrain([next_word], IAMBIC_PENTAMETER, ngram_dict, ngram_reverse_dict)
    # print(qt2)
    last_word = qt2[-1][-1]

    possible_words = get_possible_words(last_word, IAMBIC_PENTAMETER, ngram_dict)
    next_word = possible_words[0]
    qt3 = produce_quatrain([next_word], IAMBIC_PENTAMETER, ngram_dict, ngram_reverse_dict)


    # print(qt3)

    last_word = qt3[-1][-1]

    possible_words = get_possible_words(last_word, IAMBIC_PENTAMETER, ngram_dict)
    next_word = possible_words[0]

    couplet = produce_couplet([next_word], IAMBIC_PENTAMETER, ngram_dict, ngram_reverse_dict)
    # print(couplet)

    lines = qt1 + qt2 + qt3 + couplet

    qt1_str = [line_to_string(line) for line in qt1]
    qt2_str = [line_to_string(line) for line in qt2]
    qt3_str = [line_to_string(line) for line in qt3]
    c_str = [line_to_string(line) for line in couplet]

    return [qt1_str, qt2_str, qt3_str, c_str]


def produce_limerick(start:List[Word], ngram_dict:NGRAM_DICT, ngram_reverse_dict:NGRAM_DICT) -> List[Line]:

    LIMERICK1 = "010010010"
    LIMERICK2 = "0010010"
    line1 = complete_line_forward(start, LIMERICK1, ngram_dict)

    rhyme_seed = get_rhyme_word(line1[-1].spelling, LIMERICK1, ngram_reverse_dict)

    line2 = gen_line_backward(rhyme_seed, LIMERICK1, ngram_reverse_dict)


    line3 = gen_line_forward(line2[-1], LIMERICK2, ngram_reverse_dict)

    rhyme_seed = get_rhyme_word(line3[-1].spelling, LIMERICK2, ngram_reverse_dict)

    line4 = gen_line_backward(rhyme_seed, LIMERICK2, ngram_reverse_dict)

    rhyme_seed = get_rhyme_word(line4[-1].spelling, LIMERICK1, ngram_reverse_dict)
    line5 = gen_line_backward(rhyme_seed, LIMERICK1, ngram_reverse_dict)

    lines = line1 + line2 + line3 + line4 + line5
    return [line_to_string(line) for line in lines]






def produce_quatrain(start:List[Word], stress_pattern:str, ngram_dict:NGRAM_DICT, ngram_reverse_dict:NGRAM_DICT) -> List[List[Word]]:
    line1 = complete_line_forward(start, IAMBIC_PENTAMETER, ngram_dict)
    line2 = gen_line_forward(line1[-1], IAMBIC_PENTAMETER, ngram_dict)

    rhyme_seed = get_rhyme_word(line1[-1].spelling, IAMBIC_PENTAMETER[1:], ngram_reverse_dict)

    line3 = gen_line_backward(rhyme_seed, IAMBIC_PENTAMETER, ngram_reverse_dict)

    rhyme_seed = get_rhyme_word(line2[-1].spelling, IAMBIC_PENTAMETER[1:], ngram_reverse_dict)
    line4 = gen_line_backward(rhyme_seed, IAMBIC_PENTAMETER, ngram_reverse_dict)
    return [line1, line2, line3, line4]


def produce_couplet(start:List[Word], stress_pattern:str, ngram_dict:NGRAM_DICT, ngram_reverse_dict:NGRAM_DICT) -> List[List[Word]]:
    line1 = complete_line_forward(start, IAMBIC_PENTAMETER, ngram_dict)
    rhyme_seed = get_rhyme_word(line1[-1].spelling, IAMBIC_PENTAMETER[1:], ngram_reverse_dict)

    line2 = gen_line_backward(rhyme_seed, IAMBIC_PENTAMETER, ngram_reverse_dict)
    return [line1, line2]




def get_rhyme_word(token: str, stress_pattern:str, ngram_dict: NGRAM_DICT) -> Word:
    possible_rhymes = p.rhymes(token)
    filtered_rhymes = [rhyme for rhyme in possible_rhymes if rhyme in ngram_dict and word_fits_pattern(rhyme, stress_pattern, reverse=True)]
    return convert_to_word(random.choice(filtered_rhymes))


def get_remaining_stress_pattern(current_line: List[Word], stress_pattern: str, reverse:bool=False) -> str:
    current_stresses = "".join([word.stress_pattern for word in current_line])
    remaining_number_stresses = len(stress_pattern) - len(current_stresses)
    if reverse:
        remaining_stress_pattern = stress_pattern[:remaining_number_stresses]
    else:
        remaining_stress_pattern = stress_pattern[-remaining_number_stresses:]
    return remaining_stress_pattern


def complete_line_forward(current_line: List[Word], stress_pattern: str, ngram_dict: NGRAM_DICT) -> List[Word]:
    """
    stress_pattern is a constant like IAMBIC_PENTAMETER
    """

    remaining_stress_pattern = get_remaining_stress_pattern(current_line, stress_pattern)
    next_word = gen_next_word_forward(current_line[-1], remaining_stress_pattern, ngram_dict)
    if completes_line(next_word, current_line):
        return current_line + [next_word]
    else:
        new_line = current_line + [next_word]
        return complete_line_forward(new_line, stress_pattern, ngram_dict)


def complete_line_backward(current_line: List[Word], stress_pattern: str, ngram_dict: NGRAM_DICT) -> List[Word]:
    remaining_stress_pattern = get_remaining_stress_pattern(current_line, stress_pattern, True)
    possible_words = get_possible_words(current_line[0], remaining_stress_pattern, ngram_dict, True, True)
    next_word = random.choice(possible_words)


    if completes_line(next_word, current_line):
        return [next_word] + current_line
    else:
        new_line = [next_word] + current_line
        return complete_line_backward(new_line, stress_pattern, ngram_dict)


    # gen_next_word_forward(current_line[-1], remaining_stress_pattern, ngram_dict)
    # print(next_word)

    # line = complete_line_forward(current_line, stress_pattern, ngram_dict)



def gen_next_word_forward(seed: Word, remaining_stress_pattern: str, ngram_dict: NGRAM_DICT) -> Word:
    possible_words = get_possible_words(seed, remaining_stress_pattern, ngram_dict, dedup=True)
    if possible_words:
        next_word = random.choice(possible_words)
    else:
        next_word = Word("shall", "0")
    return next_word

def gen_line_forward(seed: Word, stress_pattern: str, ngram_dict: NGRAM_DICT) -> List[Word]:
    first_word = gen_next_word_forward(seed, stress_pattern, ngram_dict)
    return complete_line_forward([first_word], stress_pattern, ngram_dict)


def gen_line_backward(seed: Word, stress_pattern: str, ngram_dict: NGRAM_DICT):

    return complete_line_backward([seed], stress_pattern, ngram_dict)



def get_next_word(last_word: Word, stress_pattern:str, ngram_dict:NGRAM_DICT) -> Word:
    return random.choice(get_possible_words(last_word, stress_pattern, ngram_dict))


def filter_possible_words(possible_stresses: List[str], words: List[str]) -> List[Word]:
    """
        :type possible_stresses List[stress_strings]
        :type words List[strings]
        :filtered_words List[Word]
    """
    filtered_words = []
    for stress_pattern in possible_stresses:
        for word in words:
            if word_matches_stress(word, stress_pattern):
                filtered_words.append(Word(word, stress_pattern))

    random.shuffle(filtered_words)


    single_syllable_words = []
    for word in words:
        for stress_pattern in ["0", "1"]:
            if word_fits_pattern(word, stress_pattern):
                word_obj = Word(word, stress_pattern)
                single_syllable_words.append(word_obj)

    random.shuffle(single_syllable_words)
    return filtered_words + single_syllable_words

def one_syllable(token:str) -> bool:
    pronunciations = p.phones_for_word(token)
    for pronunciation in pronunciations:
        if len(p.stresses(pronunciation)) == 1:
            return True
    return False

def get_possible_words(seed: Word, stress_pattern: str, ngram_dict: NGRAM_DICT, dedup: bool=False, reverse:bool=False) -> List[Word]:
    if reverse:
        possible_stresses = get_possible_stresses_rev(stress_pattern)

    else:
        possible_stresses = get_possible_stresses(stress_pattern)

    candidate_words = ngram_dict.get(seed.spelling, [])

    # deduping makes the `has_path_to_rhyme` search way faster!
    if dedup:
        candidate_words = list(set(candidate_words))

    possible_words = filter_possible_words(possible_stresses, candidate_words)

    return possible_words


def has_path_to_rhyme(current_line: List[Word], rhyme_word: Word, stress_pattern: str, ngram_dict: Dict) -> bool:
    """
    Of the next possible words, are there any that satisfy these constraints:
        a. They're less than or equal to 10 syllables when added to current_line, and it has_path_to_rhyme holds on the line that results from adding it
        b. if they `complete` the line, does it rhyme with rhyme_word
    """
    seed = current_line[-1]

    remaining_stress_pattern = get_remaining_stress_pattern(current_line, stress_pattern)

    possible_words = get_possible_words(seed, remaining_stress_pattern, ngram_dict, dedup=True)

    for possible_word in possible_words:

        if completes_line(possible_word, current_line) and rhymes(possible_word, rhyme_word):
            return True
        elif incomplete_line(possible_word, current_line):
            new_line = current_line + [possible_word]
            remaining_stress_pattern = get_remaining_stress_pattern(current_line, stress_pattern)
            return has_path_to_rhyme(new_line, rhyme_word, remaining_stress_pattern, ngram_dict)

    return False


def completes_line(word: Word, current_line: List[Word]) -> bool:
    line = current_line + [word]
    return sum([len(word.stress_pattern) for word in line]) == 10


def incomplete_line(word: Word, current_line: List[Word]) -> bool:
    line = current_line + [word]
    return sum([len(word.stress_pattern) for word in line]) < 10


def rhymes(word: Word, rhyme_word: Word) -> bool:
    return word.spelling in p.rhymes(rhyme_word.spelling)

# to run the script thing
if __name__ == '__main__':
    main()
