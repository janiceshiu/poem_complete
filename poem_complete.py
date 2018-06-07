#!.env/bin/python3

import nltk as n
from typing import List, Dict
from nltk.corpus import gutenberg
from collections import defaultdict
from word import Word
from stresses import get_possible_stresses, word_matches_stress
import random
import pronouncing as p
import time
import pickle
import json

def load_or_create_ngram() -> Dict[str, List[str]]:
  try:
      with open('ngram_dict.json') as fp:
        ngram_dict = json.load(fp)
        return ngram_dict
  except FileNotFoundError:
      words = gutenberg.words()
      filtered = list(filter(lambda word: word.isalpha(), words))
      filtered_lower = [ word.lower() for word in filtered ]

      ngram_dict = defaultdict(list)
      ngrams = zip(filtered_lower, filtered_lower[1:])
      for w1, w2 in ngrams:
          ngram_dict[w1].append(w2)


      with open('ngram_dict.json', 'w') as fp:
          json.dump(ngram_dict, fp)

      return ngram_dict



def convert_to_word(token: str) -> Word:
  pass

def main():
  start = input("How should we start your poem? ").lower().strip()

  words = [convert_to_word(token) for token in start.split()]



  ngram_dict = load_or_create_ngram()

  current_line = [Word("shall", "0")]

  rhyme_word = Word("day", "1")

  start = time.time()

  print(has_path_to_rhyme(current_line, rhyme_word, ngram_dict))
  print(time.time() - start)


def get_next_word(current_word:Word, model) -> List[Word]:
    """
        :type current_word: string
        :type mode: markov_model
        :rtype: List[string]
    """
    words = model.get_next_word(current_word)
    return words

def filter_possible_words(possible_stresses: List[str], words: List[str]) -> List[Word]:
    """
        :type possible_stresses List[stress_strings]
        :type words List[strings]
        :filtered_words List[Word]
    """
    filtered_words : List[Word] = []
    for stress_pattern in possible_stresses:
        for word in words:
            if word_matches_stress(word, stress_pattern):
                filtered_words.append(Word(word, stress_pattern))
    return filtered_words

def get_possible_words(current_line:List[Word], ngram_dict:Dict[str, List[str]], dedup:bool=False) -> List[Word]:
    current_stress_str = "".join([word.stress_pattern for word in current_line])
    possible_stresses = get_possible_stresses(current_stress_str)
    candidate_words = ngram_dict.get(current_line[-1].spelling, [])

    # deduping makes the `has_path_to_rhyme` search way faster!
    if dedup:
      candidate_words = list(set(candidate_words))

    possible_words = filter_possible_words(possible_stresses, candidate_words)

    return possible_words


def has_path_to_rhyme(current_line:List[Word], rhyme_word: Word, ngram_dict:Dict) -> bool:
    """
  Of the next possible words, are there any that satisfy these constraints:
      a. They're less than or equal to 10 syllables when added to current_line, and it has_path_to_rhyme holds on the line that results from adding it
      b. if they `complete` the line, does it rhyme with rhyme_word
   """
    possible_words = get_possible_words(current_line, ngram_dict, dedup=True)

    for possible_word in possible_words:

      if completes_line(possible_word, current_line) and rhymes(possible_word, rhyme_word):
        return True
      elif incomplete_line(possible_word, current_line):
        return has_path_to_rhyme(current_line + [possible_word], rhyme_word, ngram_dict)

    return False


def completes_line(word:Word, current_line:List[Word]) -> bool:
  line = current_line + [word]
  return sum([len(word.stress_pattern) for word in line]) == 10


def incomplete_line(word:Word, current_line:List[Word]) -> bool:
  line = current_line + [word]
  return sum([len(word.stress_pattern) for word in line]) < 10

def rhymes(word:Word, rhyme_word: Word) -> bool:
  return word.spelling in p.rhymes(rhyme_word.spelling)

# to run the script thing
if __name__ == '__main__':
  main()
