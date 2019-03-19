import os, sys, time
import glob
import types
import ipywidgets as widgets
import text_corpus
import domain_logic_vatican as domain_logic
import nltk
import pandas as pd
import zipfile

sys.path = list(set(['.', '..']) - set(sys.path)) + sys.path

import common.widgets_config as widgets_config
import common.utility as utility

logger = utility.getLogger('corpus_text_analysis')

from nltk.parse import corenlp

STANFORD_CORE_NLP_URL = 'http://localhost:9000'

def merge_entities(entities):
    n_entities = len(entities)
    if n_entities <= 1:
        return entities
    merged = entities[:1]
    for doc_id, i_n, w_n, t_n in entities[1:]:
        doc_id_p, i_p, w_p, t_p = merged[-1]
        if i_n == i_p + 1 and t_n == t_p:
            merged[-1] = (doc_id, i_n, '_'.join([w_p, w_n]), t_p)
        else:
            merged.append((doc_id, i_n, w_n, t_n))
    return merged

def recognize_named_entities(tagger, doc_id, text, excludes=None):
    sentences = nltk.sent_tokenize(text)
    start_index = 0
    excludes = excludes or []
    merged_ents = []
    for sentence in sentences:
        tokens = nltk.word_tokenize(sentence)
        ents = [ (doc_id, start_index + index, word, ent_type) for index, (word, ent_type) in enumerate(tagger.tag(tokens)) if ent_type not in excludes ]
        start_index += len(sentence)
        merged_ents = merge_entities(ents)
    return merged_ents

#
#     if not os.path.isfile(targetfile) or overwrite:
#         if os.path.isfile(targetfile):
#             os.remove(targetfile)
#         with zipfile.ZipFile(targetfile, "w", compression=zipfile.ZIP_DEFLATED) as z:
#             pass
#     else:
        
#         with zipfile.ZipFile(targetfile, "r") as z:
#             zip_filenames = z.namelist()
            
#         pdf_filepaths = list(set(pdf_filepaths) - set(zip_filenames))
    
#     with zipfile.ZipFile(targetfile, "a", compression=zipfile.ZIP_DEFLATED) as z:
#         z.writestr(text_filename, pdf_text)
            
def compute_stanford_ner(source_file, service_url=STANFORD_CORE_NLP_URL, excludes=None):
    
    excludes = excludes or ('O', )
    
    assert os.path.isfile(source_file), 'File missing!'
    
    tagger = corenlp.CoreNLPParser(url=service_url, encoding='utf8', tagtype='ner')
    
    reader = text_corpus.CompressedFileReader(source_file)
    document_index = domain_logic.compile_documents_by_filename(reader.filenames)
    stream = domain_logic.get_document_stream(reader, 'en', document_index=document_index)
    
    i = 0
    ner_data = []
    for filename, text, metadata in stream:
        document_id = document_index.loc[document_index.filename == filename, 'document_id'].values[0]
        ner = recognize_named_entities(tagger, document_id, text, excludes)
        ner_data.extend(ner)
        i += 1
        if i % 10 == 0:
            logger.info('Processed {} files...'.format(i))
            #break
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
    
    lw = lambda w: widgets.Layout(width=w)
    
    corpus_files = sorted(glob.glob(os.path.join(data_folder, '*.txt.zip')))
    
    gui = types.SimpleNamespace(
        output=widgets.Output(layout={'border': '1px solid black'}),
        source_path=widgets_config.dropdown(description='Corpus', options=corpus_files, value=corpus_files[-1], layout=lw('300px')),
        compute=widgets.Button(description='Compute', button_style='Success', layout=lw('100px'))
    )
    
    display(widgets.VBox([
        widgets.HBox([
            widgets.VBox([
                gui.source_path,
            ]),
            widgets.VBox([
                gui.compute,
            ]),
        ]),
        gui.output
    ]))
    
    def compute_stanford_ner_callback(*_args):
        gui.output.clear_output()
        with gui.output:
            compute_and_store_stanford_ner(gui.source_path.value)
            #display(df)
    gui.compute.on_click(compute_stanford_ner_callback)


#data_folder = '../../data'
#display_stanford_ner_gui(data_folder)
for source_file in [ '../../data/benedict-xvi_curated_20190326.txt.zip', '../../data/francis_curated_20190326.txt.zip' ]:
    compute_and_store_stanford_ner(source_file)
    
