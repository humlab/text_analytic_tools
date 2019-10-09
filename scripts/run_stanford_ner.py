import os, sys, time
import glob
import types
import ipywidgets
import nltk
import pandas as pd

import text_analytic_tools.common.text_corpus as text_corpus
import text_analytic_tools.utility as utility

from text_analytic_tools.domain_logic_config import current_domain as domain_logic

sys.path = list(set(['.', '..']) - set(sys.path)) + sys.path

logger = utility.getLogger('corpus_text_analysis')

from nltk.parse import corenlp

STANFORD_CORE_NLP_URL = 'http://localhost:9000'

def merge_entities(entities):
    n_entities = len(entities)
    if n_entities <= 1:
        return entities
    merged = entities[:1]
    for doc_id, i_n, w_n, t_n in entities[1:]:
        _, i_p, w_p, t_p = merged[-1]
        if i_n == i_p + 1 and t_n == t_p:
            merged[-1] = (doc_id, i_n, '_'.join([w_p, w_n]), t_p)
        else:
            merged.append((doc_id, i_n, w_n, t_n))
    return merged

def recognize_named_entities(tagger, doc_id, text, excludes=None, includes=None):
    ''' excludes not used '''
    sentences = nltk.sent_tokenize(text)
    start_index = 0
    excludes = excludes or []
    includes = includes or []
    merged_ents = []
    for sentence in sentences:
        tokens = nltk.word_tokenize(sentence)
        tagged_data = tagger.tag(tokens)
        ents = [ (doc_id, start_index + index, word, ent_type) for index, (word, ent_type) \
                in enumerate(tagged_data) if ent_type in includes ]
        start_index += len(sentence)
        merged_ents.extend(merge_entities(ents))
    return merged_ents

def compute_stanford_ner(source_file, service_url=STANFORD_CORE_NLP_URL, excludes=None, includes=None):

    includes = includes or (
        'LOCATION', 'CITY', 'STATE_OR_PROVINCE', 'COUNTRY'
    )

    # For English, by default, this annotator recognizes named (PERSON, LOCATION, ORGANIZATION, MISC),
    # numerical (MONEY, NUMBER, ORDINAL, PERCENT), and temporal (DATE, TIME, DURATION, SET) entities (12 classes).
    # Adding the regexner annotator and using the supplied RegexNER pattern files adds support for the fine-grained and additional entity
    # classes EMAIL, URL, CITY, STATE_OR_PROVINCE, COUNTRY, NATIONALITY, RELIGION, (job)
    # TITLE, IDEOLOGY, CRIMINAL_CHARGE, CAUSE_OF_DEATH (11 classes) for a total of 23 classes.

    assert os.path.isfile(source_file), 'File missing!'

    tagger = corenlp.CoreNLPParser(url=service_url, encoding='utf8', tagtype='ner')
    #tokenizer = corenlp.CoreNLPParser(url=service_url, encoding='utf8')

    reader = text_corpus.CompressedFileReader(source_file)
    document_index = domain_logic.compile_documents_by_filename(reader.filenames)
    stream = domain_logic.get_document_stream(reader, 'en', document_index=document_index)

    i = 0
    ner_data = []
    for filename, text, metadata in stream:
        print(filename)
        document_id = document_index.loc[document_index.filename == filename, 'document_id'].values[0]
        ner = recognize_named_entities(tagger, document_id, text, excludes, includes)
        ner_data.extend(ner)
        i += 1
        if i % 10 == 0:
            logger.info('Processed {} files...'.format(i))
            # break

    return ner_data

def compute_and_store_stanford_ner(source_file):

    ner_data = compute_stanford_ner(source_file=source_file)

    df = pd.DataFrame(ner_data, columns=['doc_id', 'pos', 'entity', 'ent_type'])
    df.index.name = 'id'

    store_name = 'ner_{}_{}.txt'.format(
        os.path.splitext(os.path.split(source_file)[1])[0],
        time.strftime("%Y%m%d%H%M%S", time.localtime())
    )

    df.to_csv(store_name, sep='\t')
    logger.info('Result stored in %s', store_name)
    return df

def display_stanford_ner_gui(data_folder):

    lw = lambda w: ipywidgets.Layout(width=w)

    corpus_files = sorted(glob.glob(os.path.join(data_folder, '*.txt.zip')))

    gui = types.SimpleNamespace(
        output=ipywidgets.Output(layout={'border': '1px solid black'}),
        source_path=utility.widgets.dropdown(description='Corpus', options=corpus_files, value=corpus_files[-1], layout=lw('300px')),
        compute=ipywidgets.Button(description='Compute', button_style='Success', layout=lw('100px'))
    )

    display(ipywidgets.VBox([
        ipywidgets.HBox([
            ipywidgets.VBox([
                gui.source_path,
            ]),
            ipywidgets.VBox([
                gui.compute,
            ]),
        ]),
        gui.output
    ]))

    def compute_stanford_ner_callback(*_args):

        gui.output.clear_output()

        with gui.output:
            df = compute_and_store_stanford_ner(gui.source_path.value)
            display(df)

    gui.compute.on_click(compute_stanford_ner_callback)


#data_folder = '../../data'
#display_stanford_ner_gui(data_folder)
for source_file in [ '../../data/francis_curated_20190326.txt.zip', '../../data/benedict-xvi_curated_20190326.txt.zip', ]:
    compute_and_store_stanford_ner(source_file)

