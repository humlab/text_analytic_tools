# -*- coding: utf-8 -*-
from nltk.internals import find_jars_within_path
from nltk.tag import StanfordPOSTagger
from nltk import word_tokenize

import unittest

import pprint
pp = pprint.PrettyPrinter(indent=4)

class test_TaggerTestCases(unittest.TestCase):

    def test_tagger(self):

        jar = '\\usr\\stanford-postagger-full-2015-12-09\\stanford-postagger.jar'
        model = '\\usr\\stanford-postagger-full-2015-12-09\\models\\english-left3words-distsim.tagger'

        tagger = StanfordPOSTagger(model, jar)

        stanford_dir = tagger._stanford_jar[0].rpartition('\\')[0]
        stanford_jars = find_jars_within_path(stanford_dir)
        tagger._stanford_jar = ':'.join(stanford_jars)

        text = tagger.tag(word_tokenize("What's the airspeed of an unladen swallow ?"))

        self.assertTrue(text is not None)

if __name__ == '__main__':
    unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TaggerTestCases))

# funkar om man står i dir med Stanford's jar:
#     java -mx300m -cp "stanford-postagger.jar;lib/*" edu.stanford.nlp.tagger.maxent.MaxentTagger -model models\wsj-0-18-left3words-distsim.tagger -textFile sample-input.txt


