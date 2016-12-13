
from nltk.internals import find_jars_within_path
from nltk.tag import StanfordTagger
from nltk import word_tokenize
import papacy_scraper.settings as settings

class XMLStanfordPOSTagger(StanfordTagger):

    '''
    Instructions:

        1 Install latest version of Java
        2 Install http://www-nlp.stanford.edu/software/tagger.html#Download (Full)
        3 Set JAVA_HOME=C:\Program Files (x86)\Java\jre1.8.0_73 (replace version)
        4 Opt. Add stanford-postagger.jar path and */libs/* to CLASSPATH

    See base class at http://www.nltk.org/_modules/nltk/tag/stanford.html

    Stanford tagger docs: http://www-nlp.stanford.edu/software/pos-tagger-faq.shtml#f

    '''

    _SEPARATOR = '_'
    _JAR = 'stanford-postagger.jar'

    # def __init__(self, model, jar, encoding='utf8'):
    #     super(XMLStanfordPOSTagger, self).__init__(model, jar)

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

        x = self.tagger.tag(word_tokenize(text))

        return x

import xml.etree.ElementTree as xmlParser

class XMLTranslateService(object):

    def transform(self, xml_text):
        root = xmlParser.fromstring(xml_text)
        root.tag = 'corpus'
        for sentence in root.iter('sentence'):
            for word in sentence.iter('word'):
                word.tag = 'w'
                word.set('lemma', '|' + word.get('lemma') + '|')
                word.set('id', word.get('wid'))
        return root

    def as_string(self, root):
        return xmlParser.tostring(root, encoding="unicode")

class XMLTransformService(object):

    def transform(self, xml_text):
        root = xmlParser.fromstring(xml_text)
        root.tag = 'corpus'
        for sentence in root.iter('sentence'):
            for word in sentence.iter('word'):
                word.tag = 'w'
                word.set('lemma', '|' + word.get('lemma') + '|')
                word.set('id', word.get('wid'))
        return root

    def as_string(self, root):
        return xmlParser.tostring(root, encoding="unicode")

# http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
# pip install "numpy-1.11.2+mkl-cp34-cp34m-win32.whl"
# pip install scipy-0.18.1-cp34-cp34m-win32.whl
# pip install gensim

import gensim, gensim.models
from gensim import corpora
import os

class MalletServiceService(object):

    class TextListDocumentSource(object):

        def __init__(self, dictionary, document_list):

            pass

        def __iter__(self):
            
            for document in document_list:
                yield dictionary.doc2bow(document.lower().split())

    def get_mallet_path(self):

        if not 'MALLET_HOME' in os.environ:
            raise Exception('You need to set MALLET_HOME environment variable first.')

        return os.environ['MALLET_HOME'] + '/bin/mallet'

    def compute(self, document_source, options = { }):
        '''
        documents       List of documents (text blocks)
        options_
        remove_n        Filter out the ‘remove_n’ most frequent tokens that appear in the documents.
        extreme_filter  no_below, no_above, keep_n for filtering out tokens number of documents they appear in
        '''

        mallet_path = self.get_mallet_path()

        # Create a dictionary where the key is the 
        # Note: LDA uses a bag-of-word model, disregarding grammar and token sequence
        self.dictionary = corpora.Dictionary(self.documents, prune_at=options.get('prune_at'))

        if options.get('no_below') or options.get('no_above') or options.get('keep_n'):
            self.dictionary.filter_extremes(no_below=options.get('no_below'), no_above=options.get('no_above'), keep_n=options.get('keep_n'))

        if options.get('remove_n'):
            self.dictionary.filter_n_most_frequent(options.get('remove_n'))
        
        corpus = DocumentSource(dictionary, document_source) # [ dictionary.doc2bow(document) for document in documents ]

        model = gensim.models.wrappers.LdaMallet(
            mallet_path,
            corpus=corpus,
            num_topics=options.get('num_topics', 20),
            id2word=dictionary,
            prefix=options.get('store_prefix') # alpha=50, workers=4, optimize_interval=0, iterations=1000, topic_threshold=0.0 
        )

        return {
            'dictionary': dictionary,
            'corpus': corpus,
            'model': model,
            'options': options
        }