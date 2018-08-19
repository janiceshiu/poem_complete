import nltk
from typing import List, Dict
from nltk.corpus import gutenberg, brown
from collections import defaultdict
import random
import pronouncing as p
import json
import re
from subprocess import call

# random.seed(1)

NGRAM_DICT = Dict[str, List[str]]
Line = str
Word = str
Stresses = str
Stanza = List[Line]
IAMBIC_PENTAMETER = "0101010101"
FEM_IAMBIC_PENTAMETER = "01010101010"



def generate_line(
    seed: Word,
    remaining_stresses: Stresses,
    generator,
    from_rhyme=False,
    reverse=False
):
    if not remaining_stresses:
        return []

    if from_rhyme:
        reverse = True
        words = [word for word in p.rhymes(seed) if word != seed]
    else:
        words = generator.generate_candidates(seed, reverse=reverse)
    filtered = []
    single_syllable_words = []
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

        model: NGRAM_DICT = defaultdict(list)
        reverse_model: NGRAM_DICT = defaultdict(list)

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
                    json.dump(reverse_model, fp)
            with open(ngram_file_path, 'w') as fp:
                    json.dump(model, fp)

        return BigramGenerator(model, reverse_model)

    def generate_candidates(self, seed: str, reverse=False) -> List[str]:
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

    # print(list(map(len, get_possible_stresses(IAMBIC_PENTAMETER))))
    # print(words)
    corpus = gutenberg.words()
    corpus_name = 'gutenberg'

    bigram_generator = BigramGenerator.create(corpus, corpus_name)


    LIMERICK1 = "01001001"
    LIMERICK2 = "001001"

    generated = False
    while not generated:
        try:
            sonnet = []
            seed = None

            for index in range(3):
                if index == 0:
                    line1 = "recurse center".split() + generate_line("center", IAMBIC_PENTAMETER[4:], bigram_generator)
                else:
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
    for index, line in enumerate(sonnet):
        line = " ".join(line)
        if index % 4 == 0 and index > 0:
            print()
        print(line.capitalize())
        say(line)

    print("\n\n")
    return



def say(line:str):
    call(["say", line])

if __name__ == '__main__':
    main()
