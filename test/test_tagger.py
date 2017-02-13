# -*- coding: utf-8 -*-
import unittest
import os, sys
from nltk.internals import find_jars_within_path
from nltk.tag import StanfordPOSTagger
from nltk import word_tokenize

from bs4 import BeautifulSoup, SoupStrainer

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), '..'))

from papacy_scraper.spiders.parser import PapalTextItemParser

#from papacy_scraper.pos_tagger import POSTaggerService, XMLTranslateService

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
# DOS command that works (CD to tagger root):
#
#"C:\Program Files (x86)\Java\jre1.8.0_73\bin\java.exe" -mx128m -cp .\stanford-postagger.jar;.\lib\slf4j-simple.jar;.\lib\slf4j-api.jar edu.stanford.nlp.tagger.maxent.MaxentTagger -model .\models\english-bidirectional-distsim.tagger -textFile C:\Users\roma0050\AppData\Local\Temp\tmphdyghcot -outputFormat inlineXML -outputFormatOptions lemmatize -encoding utf8

    def xxtest_StanfordPOSTagger(self):

        jar = '\\usr\\stanford-postagger-full-2015-12-09\\stanford-postagger.jar'
        model = '\\usr\\stanford-postagger-full-2015-12-09\\models\\english-left3words-distsim.tagger'

        tagger = StanfordPOSTagger(model, jar)

        stanford_dir = tagger._stanford_jar[0].rpartition('\\')[0]
        stanford_jars = find_jars_within_path(stanford_dir)
        tagger._stanford_jar = ':'.join(stanford_jars)

        text = tagger.tag(word_tokenize("What's the airspeed of an unladen swallow ?"))

        self.assertTrue(text is not None)

    def xxxtest_POSTaggerService(self):
        tagger = POSTaggerService()
        output = tagger.tag(self.data)
        translator = XMLTranslateService()
        xml = translator.translate(output[0])
        #print(xml)

        print(translator.as_string(xml))

    def test_html_parser(self):
        html = '<div class="documento">\r\n    <!-- CONTENUTO DOCUMENTO -->\r\n\r\n    <!-- TESTO --> \r\n    <div class="testo">\r\n        <div class="abstract text parbase vaticanrichtext">\r\n\r\n\r\n\r\n\r\n\r\n\r\n\r\n<div class="clearfix"></div></div>\n\r\n        <div class="text parbase container vaticanrichtext">\r\n\r\n\r\n\r\n\r\n<p align="center"><font color="#663300">BENEDICT XVI </font></p> \n<p align="center"><i><font color="#663300"><b><font size="4">ANGELUS</font></b> </font></i></p> \n<p align="center"><i><font color="#663300">Feast of St Stephen<br> Monday, 26 December 2005</font></i></p> \n<p align="center">\xa0</p> \n<p><i>Dear Brothers and Sisters, </i></p> \n<p>Yesterday, after solemnly celebrating Christ\'s Birth, today we are commemorating the birth in Heaven of St Stephen, the first martyr. A special bond links these two feasts and it is summed up well in the Ambrosian liturgy by this affirmation: "Yesterday, the Lord was born on earth, that Stephen might be born in Heaven" (At the breaking of the bread). </p> \n<p>Just as Jesus on the Cross entrusted himself to the Father without reserve and pardoned those who killed him, at the moment of his death St Stephen prayed: "Lord Jesus, receive my spirit"; and further: "Lord, do not hold this sin against them" (cf. Acts 7: 59-60). Stephen was a genuine disciple of Jesus and imitated him perfectly. With Stephen began that long series of martyrs who sealed their faith by offering their lives, proclaiming with their heroic witness that God became man to open the Kingdom of Heaven to humankind. </p> \n<p>In the atmosphere of Christmas joy, the reference to the Martyr St Stephen does not seem out of place. Indeed, the shadow of the Cross was already extending over the manger in Bethlehem. <br>It was foretold by the poverty of the stable in which the infant wailed, the prophecy of Simeon concerning the sign that would be opposed and the sword destined to pierce the heart of the Virgin, and Herod\'s persecution that would make necessary the flight to Egypt. </p> \n<p>It should not come as a surprise that this Child, having grown to adulthood, would one day ask his disciples to follow him with total trust and faithfulness on the Way of the Cross. </p> \n<p>Already at the dawn of the Church, many Christians, attracted by his example and sustained by his love, were to witness to their faith by pouring out their blood. The first martyrs would be followed by others down the centuries to our day. </p> \n<p>How can we not recognize that professing the Christian faith demands the heroism of the Martyrs in our time too, in various parts of the world? Moreover, how can we not say that everywhere, even where there is no persecution, there is a high price to pay for consistently living the Gospel? </p> \n<p>Contemplating the divine Child in Mary\'s arms and looking to the example of St Stephen, let us ask God for the grace to live our faith consistently, ever ready to answer those who ask us to account for the hope that is in us (cf. I Pt 3: 15). </p> \n<hr> \n<p><b>After the Angelus: </b> </p> \n<p align="left">I greet all the English-speaking visitors present at today\'s Angelus and I wish you the joy and peace of Christmas! Through the intercession of the Martyr Saint Stephen, may Christians everywhere give clear witness to Christ, Saviour of all humanity. <br> \xa0</p> \n<p> </p> \n<p align="center"> <font color="#663300" size="3">© Copyright 2005 - Libreria Editrice Vaticana</font></p> \n<p align="center"> </p> \n<p align="center"> <font color="#663300"> </font></p>\r\n\r\n\r\n<div class="clearfix"></div></div>\n\r\n    </div>\r\n    <!-- /TESTO -->\r\n\r\n    <br style="clear: both;">\r\n    <hr>\r\n    <p align="center"><font color="#663300">© Copyright - Libreria Editrice Vaticana</font></p>\r\n\r\n    <!-- /CONTENUTO DOCUMENTO -->\r\n</div>'

        text = PapalTextItemParser.textify(html)
        print(text)

if __name__ == '__main__':
    unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TaggerTestCase))

# funkar om man står i dir med Stanford's jar:
#     java -mx300m -cp "stanford-postagger.jar;lib/*" edu.stanford.nlp.tagger.maxent.MaxentTagger -model models\wsj-0-18-left3words-distsim.tagger -textFile sample-input.txt


