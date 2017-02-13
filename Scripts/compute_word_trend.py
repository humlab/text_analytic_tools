#-*- coding: utf-8 -*-

import os
import glob
import fnmatch
import collections
import csv
import functools
import re

def load_and_compute_frequencies(options, filenames):

    def process(options, filename, wc):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                words = [ x for x in line.lower().split() if len(x) >= options["min_word_length"] ]
                wc.update(words)

    def get_key(filename):
        # FIXME: Parse year from pope split filenames
        year = re.match('\w+(\d{4})', os.path.basename(filename)).group(1)
        return year

    key_dict = { }
    for file in filenames:
        print(os.path.basename(file))
        key = get_key(file)
        if not key in key_dict:
            key_dict[key] = collections.Counter()
        process(options, file, key_dict[key])
    return sorted([ x for x in key_dict.items() ])

def normalize_frequencies(counters):
    for year, wc in counters:
        x = sum(wc.values())
        for word in wc:
            wc[word] /= x
    return counters

def remove_stop_words(counters, stop_words):
    for key, wc in counters:
        for w in stop_words: del wc[w] 
    return counters

def store_result(counters, words, filename):
    delim = ";"
    with open(filename, 'wb') as out:
        out.write(delim.join(['year', 'total'] + words).encode('utf-8'))
        out.write(u"\n".encode('utf-8'))
        for year, wc in counters:
            values = [ wc[word] for word in words ]
            out.write(delim.join([year] + [ str(sum(values)) ] + [ str(x) for x in values ]).encode('utf-8'))
            out.write(u"\n".encode('utf-8'))

def main(options):
     
    filenames = glob.glob(options["source_pattern"])

    counters = load_and_compute_frequencies(options, filenames)
    counters = remove_stop_words(counters, options["stop_words"])
    counters = normalize_frequencies(counters)

    words = options["words_of_interest"](options, counters) if hasattr(options["words_of_interest"], '__call__') else options["words_of_interest"]
    words = [ key for key, value in words ]
    store_result(counters, words, options["destination"])

if __name__ == "__main__":

    def get_most_common_words_first_year(options, counters):
        return [ x for x, y in counters[0][1].most_common(options["word_count"]) ]

    # def get_most_common_words_all_time(options, counters):
    #     X = collections.Counter() 
    #     for year, wc in counters:
    #         X += wc
    #     return X.most_common(options["word_count"])

    def get_god(options, counters):
        # FIXME
        words = [ 'god', 'environment']
        return [ (x, 0) for x in words ]

    def read_stop_words(filename):

        with open(filename, 'r', encoding='utf-8') as file:
            return file.readlines()

    options = {           
        "source_pattern": "C:\\Temp\\pope\\splits\\*.txt",
        "destination": "C:\\Temp\\pope\\splits\\trends\\most_common_words_first_year.csv",   
        "stop_words": [], # read_stop_words(filename)
        "min_word_length": 2,
        "word_count": 20,
        "words_of_interest": get_god # [] 
    }
    main(options)
