import zipfile
import os, io, time
from nltk.tokenize.stanford import CoreNLPTokenizer

def main(options):

    # https://stackoverflow.com/questions/45663121/about-stanford-word-segmenter
    # curl -O https://nlp.stanford.edu/software/stanford-corenlp-full-2016-10-31.zip
    # unzip stanford-corenlp-full-2016-10-31.zip && cd stanford-corenlp-full-2016-10-31
    #
    # java -Xmx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer
    #  -preload tokenize,ssplit,pos,lemma,ner,parse \
    #  -status_port 9001  -port 9001 -timeout 15000


    tokenizer = CoreNLPTokenizer('http://localhost:9001')
    for zip_source in options["zip_sources"]:
        outfilename = os.path.join('..\\data', os.path.basename(zip_source)[:-4] + "_word_count.csv")
        outfilename = outfilename.replace('_text', '')
        with io.open(outfilename, 'w', encoding='utf8') as o:
            with zipfile.ZipFile(zip_source) as pope_zip:
                for filename in pope_zip.namelist():
                    with pope_zip.open(filename, 'r') as pope_file:
                        content = pope_file.read().decode('utf8')
                        try:
                            token_count = len(tokenizer.tokenize(content))
                        except:
                            token_count = len(content.split())
                            print("Failed: {} {}".format(filename, token_count))
                        o.write('{};{};{}\n'.format(filename, len(content), token_count))

if __name__ == "__main__":

    options = {
        "zip_sources": [ "..\\data\\benedict-xvi_text.zip", "..\\data\\francesco_text.zip", "..\\data\\john-paul-ii_text.zip" ],
        "ner_path":  "c:\\Usr\\stanford-ner-2016-10-31\\",
        'ner_model': 'english.all.3class.distsim.crf.ser.gz'
    }

    os.environ['STANFORD_MODELS'] = os.path.join(options["ner_path"], "classifiers")
    os.environ['JAVAHOME'] = 'C:\\Program Files\\Java\\jre1.8.0_141'
    os.environ['CLASSPATH'] = os.path.join(options["ner_path"], "stanford-ner.jar") + \
        ";"  + os.path.join("C:\\Usr\\stanford-postagger-full-2015-12-09", "stanford-postagger.jar")

    main(options)
