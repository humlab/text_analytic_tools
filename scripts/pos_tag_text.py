#-*- coding: utf-8 -*-

import os, io, glob, codecs, logging
from nltk.tag import StanfordTagger
from nltk import word_tokenize
import xml.etree.ElementTree as xmlParser

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

    def __init__(self, model_filename, path_to_jar=None, encoding='utf8', verbose=False, java_options='-mx1200m'):
         super(XMLStanfordPOSTagger, self).__init__(model_filename, path_to_jar, encoding, verbose, java_options)

    @property
    def _cmd(self):
        return [
            'edu.stanford.nlp.tagger.maxent.MaxentTagger',
            '-model', self._stanford_model,
            '-textFile', self._input_file_path,
            '-outputFormat', 'inlineXML',
            '-outputFormatOptions', 'lemmatize'
        ]

    def parse_output(self, text, sentences = None):
        return [ [ text ] ]

class POSTaggerService(object):

    def __init__(self, options):

        self.jar = options["tagger_jar"]
        self.model = options["tagger_model"]
        self.tagger = XMLStanfordPOSTagger(self.model, self.jar)

    def tag(self, text):
        try:
            x = self.tagger.tag(word_tokenize(text))
            return x[0] if isinstance(x,list) else x
        except Exception as x:
            #print(x)
            return None

#"C:\\Program Files (x86)\\Java\\jre1.8.0_73\\bin\\java.exe" -mx128m -cp \\usr\\stanford-postagger-full-2015-12-09\\stanford-postagger.jar edu.stanford.nlp.tagger.maxent.MaxentTagger -model \\usr\\stanford-postagger-full-2015-12-09\\models\\english-bidirectional-distsim.tagger -textFile #C:\\Users\\roma0050\\AppData\\Local\\Temp\\tmphdyghcot -outputFormat inlineXML -outputFormatOptions lemmatize -encoding utf8

class XMLTranslateService(object):

    def translate(self, xml_text):
        root = xmlParser.fromstring(xml_text)
        root.tag = 'corpus'
        root.set('id', '0')
        for sentence in root.iter('sentence'):
            for word in sentence.iter('word'):
                word.tag = 'w'
                word.set('lemma', '|' + word.get('lemma') + '|')
                word.set('id', word.get('wid'))
        return root

    def as_string(self, root):
        return xmlParser.tostring(root, encoding="unicode")

class TextService():

    @staticmethod
    def replaceExt(filename, replace_ext):
        basename = os.path.splitext(filename)[0]
        folder = os.path.dirname(filename)
        return os.path.join(os.path.dirname(filename), '{0}.{1}'.format(basename.replace('/','_'), replace_ext))

    @staticmethod
    def write(filename, data):
        with io.open(filename,'w',encoding='utf8') as f:
            f.write(data)
        logging.info('Stored item in {0}'.format(filename))

    @staticmethod
    def read(filename):
        with codecs.open(filename, "r", "utf-8") as f:
            return f.read()

def main(options):
     
    filenames = glob.glob(options["source"])
    tagger = POSTaggerService(options)
    translator = XMLTranslateService()

    for filename in filenames:

        outfile = TextService.replaceExt(filename, "xml")
        if os.path.isfile(outfile):
            #print("Skipping (exists) {0}".format(outfile))
            continue

        #print (filename)
        text = TextService.read(filename)
        #print(TextService.replaceExt(filename, "xml"))

        xml = tagger.tag(text)

        if xml is None:
            print("FAILED ({0}".format(filename))
            continue
        #print(xml)

        xml = translator.translate(xml)
        #print(xml)

        TextService.write(outfile, translator.as_string(xml))

if __name__ == "__main__":

    options = {           
        "source": "C:\\tmp\\output\\john-paul-ii\\*.txt",
        "tagger_jar": '\\usr\\stanford-postagger-full-2015-12-09\\stanford-postagger.jar',
        "tagger_model": '\\usr\\stanford-postagger-full-2015-12-09\\models\\english-bidirectional-distsim.tagger'
    }

    main(options)
