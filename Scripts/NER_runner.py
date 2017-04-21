import os, glob, io, codecs, time
import collections
from nltk.tag import StanfordNERTagger
from nltk.tokenize import StanfordTokenizer

def main(options):

    filenames = glob.glob(options["source"])

    nerrer = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz', os.path.join(options["ner_path"], "stanford-ner.jar"))
    tokenizer = StanfordTokenizer()

    outfile = "output_" + time.strftime("%Y%m%d_%H%M%S") + ".csv"

    with io.open(outfile, 'w', encoding='utf8') as o:
        for filename in filenames:
            with codecs.open(filename, "r", "utf-8") as f: text = f.read()
            tokens = tokenizer.tokenize(text)
            data = nerrer.tag(tokens)
            #print(data)
            # TODO Merge adjacent words with same classifier
            entities = [ (word, wclass) for (word, wclass) in data  ] # if wclass == 'LOCATION' or wclass == 'PERSON'
            wc = collections.Counter()
            wc.update(entities)
            document_name = os.path.basename(os.path.splitext(filename)[0])
            pope, lang, genre, *tail = document_name.split('_')
            year = next(x for x in tail if x.isnumeric() and len(x) == 4)
            ner_data = [ (document_name, year, genre, pope, word, wclass, wc[(word, wclass) ]) for (word, wclass) in wc]
            o.write('\n'.join(map(lambda x : ';'.join([str(y) for y in x]), ner_data)))
            o.write('\n')


if __name__ == "__main__":

    os.environ['STANFORD_MODELS'] = os.path.join(options["ner_path"], "classifiers")
    os.environ['JAVAHOME'] = 'C:\\Program Files\\Java\\jre1.8.0_121'
    os.environ['CLASSPATH'] = os.path.join(options["ner_path"], "stanford-ner.jar") + ";"  + os.path.join("C:\\Usr\\stanford-postagger-full-2015-12-09", "stanford-postagger.jar") 

    options = {
        "source": "c:\\Temp\\ner_data\\Test\\*.txt",
        "ner_path":  "c:\\Usr\\stanford-ner-2016-10-31\\"
    }

    main(options)
