
import nltk as n
from typing import List
from nltk.corpus import gutenberg
from collections import defaultdict
from word import Word
from stresses import get_possible_stresses
import random

# to run the script thing
# if __name__ == '__main__':
#   main()

def main():
  words = gutenberg.words()
  filtered = list(filter(lambda word: word.isalpha(), words))
  filtered_lower = [ word.lower() for word in filtered ]

  ngram_dict = defaultdict(list)
  ngrams = zip(filtered_lower, filtered_lower[1:])
  for w1, w2 in ngrams:
    ngram_dict[w1].append(w2)

  # return (filtered_lower, ngram_dict)

def get_next_word(current_word, model):
    """
        :type current_word: string
        :type mode: markov_model
        :rtype: List[string]
    """
    words = model.get_next_word(current_word)
    return words

def filter_possible_words(possible_stresses: List[str], words: List[str]) -> List[str]:
    """
        :type possible_stresses List[stress_strings]
        :type words List[strings]
        :filtered_words List[strings]
    """
    filtered_words = []
    for stress_pattern in possible_stresses:
        for word in words:
            if word_matches_stress(word, stress_pattern):
                filtered_words.append(word)
    return filtered_words

def get_possible_words(current_line:List[str], current_stress_str: str, ngram_dict) -> List[Word]:
    possible_stresses = get_possible_stresses(current_stress_str)
    candidate_words = ngram_dict.get(current_line[-1], [])
    possible_words = filter_possible_words(possible_stresses, candidate_words)

    return possible_words
