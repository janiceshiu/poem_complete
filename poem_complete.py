import nltk
from typing import List, Dict
from nltk.corpus import gutenberg, brown
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
FEM_IAMBIC_PENTAMETER = "01010101010"



def generate_line(seed, remaining_stresses, generator, from_rhyme=False, reverse=False):
    if not remaining_stresses:
        return []

    if from_rhyme:
        words = [word for word in p.rhymes(seed) if word != seed]
    else:
        words = generator.generate_candidates(seed, reverse=reverse)
    filtered = []
    single_syllable_words = []
    # import ipdb; ipdb.set_trace()
    for word in words:
        if not generator.word_in_model(word):
            continue
        for stress_pattern in get_stress_patterns(word):
            if reverse and remaining_stresses.endswith(stress_pattern):
                filtered.append((word, remaining_stresses[:-len(stress_pattern)]))
            elif reverse and len(stress_pattern) == 1:
                single_syllable_words.append((word, remaining_stresses[:-1]))

            elif remaining_stresses.startswith(stress_pattern):
                filtered.append((word, remaining_stresses[len(stress_pattern):]))

            elif len(stress_pattern) == 1:
                single_syllable_words.append((word, remaining_stresses[1:]))

    random.shuffle(filtered)
    random.shuffle(single_syllable_words)
    words = filtered + single_syllable_words

    next_word, remaining_stresses = words[0]
    rest_of_line = generate_line(next_word, remaining_stresses, generator, reverse=reverse)
    if reverse:
        return rest_of_line + [next_word]
    return [next_word] + rest_of_line


def get_stress_patterns(word):
    pronunciations = p.phones_for_word(word)
    stress_patterns = [p.stresses(pronunciation).replace("2", "1")
                       for pronunciation in pronunciations]
    # if not stress_patterns:
    #     # pick one arbitrarily
    #     number_syllables_guess = len(re.findall(r"[aeiou]+", word))
    #     d, m = divmod(number_syllables_guess, 2)
    #     return [d * "01" +  m * "0"]
    return stress_patterns


class BigramGenerator:
    def __init__(self, model, reverse_model):
        self.model = model
        self.reverse_model = reverse_model

    @classmethod
    def create(cls, corpus: List[str], corpus_name: str):
        folder = "ngrams"
        ngram_file_path = "{}/{}_ngram_dict.json".format(folder, corpus_name)
        reverse_ngram_file_path = "{}/{}_reverse_ngram_dict.json".format(folder, corpus_name)

        model = defaultdict(list)
        reverse_model = defaultdict(list)

        try:
            with open(ngram_file_path) as fp:
                model = json.load(fp)
            with open(reverse_ngram_file_path) as fp:
                reverse_model = json.load(fp)
        except FileNotFoundError:
            words = [word.lower() for word in corpus if word.isalpha()]
            bigrams = zip(words, words[1:])

            for w1, w2 in bigrams:
                model[w1].append(w2)
                reverse_model[w2].append(w1)

            with open(reverse_ngram_file_path, 'w') as fp:
                    json.dump(ngram_dict, fp)
            with open(ngram_file_path, 'w') as fp:
                    json.dump(ngram_dict, fp)

        return BigramGenerator(model, reverse_model)

    def generate_candidates(self, seed: str, reverse=False) -> [str]:
        model = self.model
        if reverse:
            model = self.reverse_model
        return model[seed]

    def word_in_model(self, word, reverse=False) -> bool:
        model = self.model
        if reverse:
            model = self.reverse_model
        return word in model



def main():
    # start = input("How should we start your poem? ").lower().strip()

    start_sonnet = "Recurse Center".lower().strip()

    # start_limerick = "There once was a".lower().strip()

    words = nltk.tokenize.word_tokenize(start_sonnet)


    # print(list(map(len, get_possible_stresses(IAMBIC_PENTAMETER))))
    # print(words)
    corpus = gutenberg.words()
    corpus_name = 'gutenberg'

    bigram_generator = BigramGenerator.create(corpus, corpus_name)


    LIMERICK1 = "01001001"
    LIMERICK2 = "001001"

    seed = "day"
    generated = False
    while not generated:
        try:
            sonnet = []
            seed = None

            for __ in range(3):
                if not seed:
                    seed = "if"
                line1 = generate_line(seed, IAMBIC_PENTAMETER, bigram_generator)
                line2 = generate_line(
                    line1[-1], IAMBIC_PENTAMETER, bigram_generator)
                line3 = generate_line(line1[-1], IAMBIC_PENTAMETER, bigram_generator, from_rhyme=True, reverse=True)
                line4 = generate_line(
                    line2[-1], IAMBIC_PENTAMETER, bigram_generator, from_rhyme=True, reverse=True)

                seed = line4[-1]
                sonnet += [line1, line2, line3, line4]

            line13 = generate_line(seed, IAMBIC_PENTAMETER, bigram_generator)
            sonnet.append(line13)
            sonnet.append(generate_line(line13[-1], IAMBIC_PENTAMETER, bigram_generator, from_rhyme=True, reverse=True))
            generated = True
        except IndexError:
            print('Still thinking...')


    call(["clear"])
    print('A Sonnet\n')
    for line in sonnet:
        line = " ".join(line)
        print(line.capitalize())
        say(line)

    return


    # start_limerick = "There once was a".lower().strip()
    # words = [convert_to_word(token) for token in nltk.tokenize.word_tokenize(start_limerick)]


    # print("\n\n\n")
    # for line in produce_limerick(words, ngram_dict, ngram_reverse_dict):
    #     print(line)
        # say(line)



def say(line:str):
    call(["say", line])



def line_to_string(line:List[Word]) -> Line:
    return " ".join(word.spelling for word in line)


def produce_sonnet(start:List[Word], stress_pattern:str, ngram_dict:NGRAM_DICT, ngram_reverse_dict:NGRAM_DICT) -> List[Stanza]:

    qt1 = produce_quatrain(start, stress_pattern, ngram_dict, ngram_reverse_dict)

    # print(qt1)

    last_word = qt1[-1][-1]
    possible_words = get_possible_words(last_word, stress_pattern, ngram_dict)
    next_word = possible_words[0]
    qt2 = produce_quatrain([next_word], stress_pattern, ngram_dict, ngram_reverse_dict)
    # print(qt2)
    last_word = qt2[-1][-1]

    possible_words = get_possible_words(last_word, stress_pattern, ngram_dict)
    next_word = possible_words[0]
    qt3 = produce_quatrain([next_word], stress_pattern, ngram_dict, ngram_reverse_dict)


    # print(qt3)

    last_word = qt3[-1][-1]

    possible_words = get_possible_words(last_word, stress_pattern, ngram_dict)
    next_word = possible_words[0]

    couplet = produce_couplet([next_word], stress_pattern, ngram_dict, ngram_reverse_dict)
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
    print(line1)

    rhyme_seed = get_rhyme_word(line1[-1].spelling, LIMERICK1, ngram_reverse_dict)
    print(rhyme_seed)
    line2 = gen_line_backward(rhyme_seed, LIMERICK1, ngram_reverse_dict)
    print(line2)

    line3 = gen_line_forward(line2[-1], LIMERICK2, ngram_reverse_dict)
    print(line3)

    rhyme_seed = get_rhyme_word(line3[-1].spelling, LIMERICK2, ngram_reverse_dict)
    print(rhyme_seed)
    line4 = gen_line_backward(rhyme_seed, LIMERICK2, ngram_reverse_dict)
    print(line4)

    rhyme_seed = get_rhyme_word(line4[-1].spelling, LIMERICK1, ngram_reverse_dict)
    print(rhyme_seed)
    line5 = gen_line_backward(rhyme_seed, LIMERICK1, ngram_reverse_dict)
    print(line5)



    lines = line1 + line2 + line3 + line4 + line5
    return [line_to_string(line) for line in lines]






def produce_quatrain(start:List[Word], stress_pattern:str, ngram_dict:NGRAM_DICT, ngram_reverse_dict:NGRAM_DICT) -> List[List[Word]]:
    line1 = complete_line_forward(start, stress_pattern, ngram_dict)
    line2 = gen_line_forward(line1[-1], stress_pattern, ngram_dict)

    rhyme_seed = get_rhyme_word(line1[-1].spelling, stress_pattern, ngram_reverse_dict)

    line3 = gen_line_backward(rhyme_seed, stress_pattern, ngram_reverse_dict)

    rhyme_seed = get_rhyme_word(line2[-1].spelling, stress_pattern, ngram_reverse_dict)
    line4 = gen_line_backward(rhyme_seed, stress_pattern, ngram_reverse_dict)
    return [line1, line2, line3, line4]


def produce_couplet(start:List[Word], stress_pattern:str, ngram_dict:NGRAM_DICT, ngram_reverse_dict:NGRAM_DICT) -> List[List[Word]]:
    line1 = complete_line_forward(start, stress_pattern, ngram_dict)
    rhyme_seed = get_rhyme_word(line1[-1].spelling, stress_pattern, ngram_reverse_dict)

    line2 = gen_line_backward(rhyme_seed, stress_pattern, ngram_reverse_dict)
    return [line1, line2]




def get_rhyme_word(token: str, stress_pattern:str, ngram_dict: NGRAM_DICT) -> Word:
    possible_rhymes = p.rhymes(token)
    filtered_rhymes = [rhyme for rhyme in possible_rhymes if rhyme in ngram_dict and word_fits_pattern(rhyme, stress_pattern, reverse=True)]

    # if not filtered_rhymes:
    #     print(len([rhyme for rhyme in possible_rhymes if rhyme in ngram_dict]))

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
    if completes_line(next_word, current_line, stress_pattern):
        return current_line + [next_word]
    else:
        new_line = current_line + [next_word]
        return complete_line_forward(new_line, stress_pattern, ngram_dict)


def complete_line_backward(current_line: List[Word], stress_pattern: str, ngram_dict: NGRAM_DICT) -> List[Word]:
    remaining_stress_pattern = get_remaining_stress_pattern(current_line, stress_pattern, True)
    possible_words = get_possible_words(current_line[0], remaining_stress_pattern, ngram_dict, True, True)
    next_word = possible_words[0]


    if completes_line(next_word, current_line, stress_pattern):
        return [next_word] + current_line
    elif incomplete_line(next_word, current_line, stress_pattern):
        new_line = [next_word] + current_line
        return complete_line_backward(new_line, stress_pattern, ngram_dict)
    else:
        return [next_word] + current_line


    # gen_next_word_forward(current_line[-1], remaining_stress_pattern, ngram_dict)
    # print(next_word)

    # line = complete_line_forward(current_line, stress_pattern, ngram_dict)



def gen_next_word_forward(seed: Word, remaining_stress_pattern: str, ngram_dict: NGRAM_DICT) -> Word:
    possible_words = get_possible_words(seed, remaining_stress_pattern, ngram_dict, dedup=True)
    # if possible_words:
    next_word = possible_words[0]
    # else:
    #     next_word = Word("shall", "0")
    return next_word

def gen_line_forward(seed: Word, stress_pattern: str, ngram_dict: NGRAM_DICT) -> List[Word]:
    first_word = gen_next_word_forward(seed, stress_pattern, ngram_dict)
    return complete_line_forward([first_word], stress_pattern, ngram_dict)


def gen_line_backward(seed: Word, stress_pattern: str, ngram_dict: NGRAM_DICT):

    return complete_line_backward([seed], stress_pattern, ngram_dict)



def get_next_word(last_word: Word, stress_pattern:str, ngram_dict:NGRAM_DICT) -> Word:
    return get_possible_words(last_word, stress_pattern, ngram_dict)[0]


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

        if completes_line(possible_word, current_line, stress_pattern) and rhymes(possible_word, rhyme_word):
            return True
        elif incomplete_line(possible_word, current_line, stress_pattern):
            new_line = current_line + [possible_word]
            remaining_stress_pattern = get_remaining_stress_pattern(current_line, stress_pattern)
            return has_path_to_rhyme(new_line, rhyme_word, remaining_stress_pattern, ngram_dict)

    return False


def completes_line(word: Word, current_line: List[Word], stress_pattern:str) -> bool:
    line = current_line + [word]
    return sum([len(word.stress_pattern) for word in line]) == len(stress_pattern)


def incomplete_line(word: Word, current_line: List[Word], stress_pattern:str) -> bool:
    line = current_line + [word]
    return sum([len(word.stress_pattern) for word in line]) < len(stress_pattern)


def rhymes(word: Word, rhyme_word: Word) -> bool:
    return word.spelling in p.rhymes(rhyme_word.spelling)

# to run the script thing
if __name__ == '__main__':
    main()
