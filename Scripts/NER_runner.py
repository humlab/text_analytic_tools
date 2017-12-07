import os, glob, io, codecs, time
import collections
from nltk.tag import StanfordNERTagger
from nltk.tokenize import StanfordTokenizer
import re

def extract_entity_phrases(data, classes = [ 'LOCATION', 'PERSON']):

    # Extract entities of selected classes, add index to enable merge to phrases
    entities = [ (i, word, wclass)
        for (i, (word, wclass)) in enumerate(data)
            if wclass in classes ]

    # Merge adjacent entities having the same classifier
    for i in range(len(entities) - 1, 0, -1):
        if entities[i][0] == entities[i-1][0] + 1 and entities[i][2] == entities[i-1][2]:
            entities[i-1] = (entities[i-1][0], entities[i-1][1] + " " + entities[i][1], entities[i-1][2])
            del entities[i]

    # Remove index in returned data
    return [ (word, wclass) for (i, word, wclass) in entities  ]

def extract_document_info(filename):
    document_name = os.path.basename(os.path.splitext(filename)[0])
    pope, lang, genre, *tail = document_name.split('_')
    try:
        year = next((x for x in tail if x.isnumeric() and len(x) == 4), '0')
        if (year == '0'):
            for item in tail:
                item_split = re.split(r'[_\-\.]', item)
                year = next((x[-4:] for x in item_split if x.isnumeric() and (len(x) == 4 or len(x) == 8)), '0')
                if year != '0':
                    break
    except:
        year = '0'
        print('Parse YEAR failed: {0}'.format(filename))

    return (document_name, pope, lang, genre, year)

def create_ner_tagger(options):
    return StanfordNERTagger(options['ner_model'], os.path.join(options["ner_path"], "stanford-ner.jar"))

def create_tokenizer(options):
    return StanfordTokenizer()

def read_file(filename):
    with codecs.open(filename, "r", "utf-8") as f:
        return f.read()

def create_statistics(entities):
    wc = collections.Counter()
    wc.update(entities)
    return wc

def serialize_content(stats, filename):
    document_name, pope, lang, genre, year = extract_document_info(filename)
    data = [ (document_name, year, genre, pope, word, wclass, stats[(word, wclass)]) for (word, wclass) in stats  ]
    content = '\n'.join(map(lambda x : ';'.join([str(y) for y in x]), data))
    return content

def write_content(outfile, content):
    if content != '':
        outfile.write(content)
        outfile.write('\n')

def main(options):

    filenames   = glob.glob(options["source"])
    nerrer      = create_ner_tagger(options)
    tokenizer   = create_tokenizer(options)
    outfile     = os.path.join(options['output_folder'], "output_" + time.strftime("%Y%m%d_%H%M%S") + ".csv")

    with io.open(outfile, 'w', encoding='utf8') as o:

        for filename in filenames:

            text        = read_file(filename)
            tokens      = tokenizer.tokenize(text)
            data        = nerrer.tag(tokens)
            entities    = extract_entity_phrases(data,  [ 'LOCATION', 'PERSON', 'ORGANIZATION' ])
            statistics  = create_statistics(entities)
            content     = serialize_content(statistics, filename)

            write_content(o, content)

if __name__ == "__main__":

    options = {
        "source": "c:\\Temp\\papacy_ner_data\\input\*.txt",
        "ner_path":  "c:\\Usr\\stanford-ner-2016-10-31\\",
        'ner_model': 'english.all.3class.distsim.crf.ser.gz',
        'output_folder': 'c:\\Temp\\papacy_ner_data\\output'
    }

    os.environ['STANFORD_MODELS'] = os.path.join(options["ner_path"], "classifiers")
    os.environ['JAVAHOME'] = 'C:\\Program Files\\Java\\jre1.8.0_141'
    os.environ['CLASSPATH'] = os.path.join(options["ner_path"], "stanford-ner.jar") + \
        ";"  + os.path.join("C:\\Usr\\stanford-postagger-full-2015-12-09", "stanford-postagger.jar")

    main(options)
