# -*- coding: utf-8 -*-
import unittest
import os, sys
from nltk.internals import find_jars_within_path
from nltk.tag import StanfordPOSTagger
from nltk import word_tokenize

sys.path.insert(0, os.getcwd())

from papacy_scraper.pos_tagger import POSTaggerService, XMLTranslateService

class TaggerTestCase(unittest.TestCase):

    def setUp(self):

        self.data = '\
            Airbus says it has turned the corner after a crisis connected to production problems and turmoil in the boardroom at its A380 super-jumbo project that has gone on for the past year. Speaking at the Paris air show, Louis Gallois, CEO of the European planemaker, said, \"Airbus is back.\"\
            Airbus, which announced a raft of orders on the first day of the show, is competing with Boeing, its American rival, for the title of the largest planemaker in the world.\
            Boeing is expected to reveal the numbers of orders for its 787 Dreamliner soon. Airbus orders unveiled on Monday included Qatar Airways confirming a $16bn order for 80 A350 Airbus planes and ordering three A380 super-jumbos for about $750m.\
            Boeing and Airbus are also competing for orders from aircraft leasing firms. Orders from these companies - who rank highly among the biggest global buyers of aircraft - are often regarded as an indication of how successful a model will be in the long term.\
            Airbus also secured orders from US Airways that are worth $10bn for 22 of its A350 jets, 60 A320s and ten of its A330-200 wide-body planes.\
            A few months ago, Airbus unveiled a major cost-cutting programme aiming to reduce the workforce in Europe by 10,000, as well as announcing a group restructuring. \"I can tell you with full confidence that Airbus is back and fully back, as you have started noting yesterday as demonstrated by our\ first day announcements,\" said Mr Gallois on the second day of the air show. \
            However, Boeing also announced a deal with General Electric (GE) on the show\'s first day. GE\'s commercial aviation services placed an order for six 777 Boeing freighters valued at around $1.4bn, to be delivered in the last quarter of 2008.\
            A Wall Street Journal website report, quoting the Delta operating chief yesterday said that Delta Air Lines were on the verge of ordering as many as 125 Boeing 787 jetliners by the end of this year. However, a spokesman for Delta later said that it had been having conversations \"with several\ aircraft makers\" and that \"no final decision\" had been made on future fleet pur-\
            chases.\
        '

    def xxtest_StanfordPOSTagger(self):

        jar = '\\usr\\stanford-postagger-full-2015-12-09\\stanford-postagger.jar'
        model = '\\usr\\stanford-postagger-full-2015-12-09\\models\\english-left3words-distsim.tagger'

        tagger = StanfordPOSTagger(model, jar)

        stanford_dir = tagger._stanford_jar[0].rpartition('\\')[0]
        stanford_jars = find_jars_within_path(stanford_dir)
        tagger._stanford_jar = ':'.join(stanford_jars)

        text = tagger.tag(word_tokenize("What's the airspeed of an unladen swallow ?"))

        self.assertTrue(text is not None)

    def test_POSTaggerService(self):
        tagger = POSTaggerService()
        output = tagger.tag(self.data)
        translator = XMLTranslateService()
        xml = translator.translate(output[0])
        #print(xml)

        print(translator.as_string(xml))

if __name__ == '__main__':
    unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TaggerTestCase))

# funkar om man står i dir med Stanford's jar:
#     java -mx300m -cp "stanford-postagger.jar;lib/*" edu.stanford.nlp.tagger.maxent.MaxentTagger -model models\wsj-0-18-left3words-distsim.tagger -textFile sample-input.txt


