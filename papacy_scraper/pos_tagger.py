
from nltk.internals import find_jars_within_path
from nltk.tag import StanfordTagger
from nltk import word_tokenize
import papacy_scraper.settings as settings

class XMLStanfordPOSTagger(StanfordTagger):

    '''
    Instructions:

        1 Install latest version of Java https://www.java.com/sv/download/help/index_installing.xml
        2 Install http://www-nlp.stanford.edu/software/tagger.html#Download (Full)
        3 Set JAVA_HOME=C:\Program Files\Java\jre1.8.0_111 (replace version)
        4 Install gensim
           4.1 pip install numpy
               Win 10: download and install numpy+mkl from  http://www.lfd.uci.edu/~gohlke/pythonlibs/
           4.1 pip install scipy
               Win 10: download and install scipy from  http://www.lfd.uci.edu/~gohlke/pythonlibs/
           4.3 pip install gensim
        5 Opt. Add stanford-postagger.jar path and */libs/* to CLASSPATH

    See base class at http://www.nltk.org/_modules/nltk/tag/stanford.html

    Stanford tagger docs: http://www-nlp.stanford.edu/software/pos-tagger-faq.shtml#f

    '''

    _SEPARATOR = '_'
    _JAR = 'stanford-postagger.jar'

     def __init__(self, model_filename, path_to_jar=None, encoding='utf8', verbose=False, java_options='-mx2000m')
         super(XMLStanfordPOSTagger, self).__init__(model, model_filename, path_to_jar, encoding, verbose, java_options)

    @property
    def _cmd(self):
        return ['edu.stanford.nlp.tagger.maxent.MaxentTagger',
                '-model', self._stanford_model,
                '-textFile', self._input_file_path,
                '-outputFormat', 'inlineXML',
                '-outputFormatOptions', 'lemmatize'
        ]

    def parse_output(self, text, sentences = None):
        return [ [ text ] ]

class POSTaggerService(object):

    def __init__(self):

        self.jar = settings.TAGGER_JAR
        self.model = settings.TAGGER_MODEL

        self.tagger = XMLStanfordPOSTagger(self.model, self.jar)

    def tag(self, text):

        try:
            x = self.tagger.tag(word_tokenize(text))

            return x[0] if isinstance(x,list) else x

        except Exception as x:
            #print(x)
            return None

import xml.etree.ElementTree as xmlParser

class XMLTranslateService(object):

    def translate(self, xml_text):
        root = xmlParser.fromstring(xml_text)
        root.tag = 'corpus'
        root.set('id', '2010')
        for sentence in root.iter('sentence'):
            for word in sentence.iter('word'):
                word.tag = 'w'
                word.set('lemma', '|' + word.get('lemma') + '|')
                word.set('id', word.get('wid'))
        return root

    def as_string(self, root):
        return xmlParser.tostring(root, encoding="unicode")

# class XMLTransformService(object):

#     def transform(self, xml_text):
#         root = xmlParser.fromstring(xml_text)
#         root.tag = 'corpus'
#         for sentence in root.iter('sentence'):
#             for word in sentence.iter('word'):
#                 word.tag = 'w'
#                 word.set('lemma', '|' + word.get('lemma') + '|')
#                 word.set('id', word.get('wid'))
#         return root

#     def as_string(self, root):
#         return xmlParser.tostring(root, encoding="unicode")
        print(translator.as_string(xml))
