import spacy
import logging
import pandas as pd
import text_analytic_tools.common.textacy_utility as textacy_utility
import text_analytic_tools.common.text_corpus as text_corpus

from text_analytic_tools.domain_logic_config import current_domain as domain_logic

logger = logging.getLogger('ner')
logger.setLevel(logging.INFO)

DEL_CRAP_CHARS = str.maketrans('', '', '"\n\t')

def get_doc_places(doc):
    return ( (w.text, w.lemma_, str(w.lemma_).translate(DEL_CRAP_CHARS), w[0].ent_type_)
                for w in doc.ents if w[0].ent_type_ in ['LOC', 'GPE'] and w.lemma_.strip() != '' )

def create_source_stream(source_path, lang, document_index=None):
    reader = text_corpus.CompressedFileReader(source_path)
    stream = domain_logic.get_document_stream(reader, lang, document_index=document_index)
    return stream

def create_nlp(model='en_core_web_sm', disable=None):
    nlp = spacy.load(model, disable=disable)
    #lang = textacy.load_spacy_lang(model, disable=disable)
    nlp.tokenizer = textacy_utility.keep_hyphen_tokenizer(nlp)
    return nlp

source_paths = [ '../../data/benedict-xvi_curated_20190326.txt_preprocessed.zip', '../../data/francis_curated_20190326.txt_preprocessed.zip' ]

model_name = 'en_core_web_lg'

logger.info('Loading model %s' % model_name)
nlp = create_nlp(model=model_name, disable=('tagger', 'parser', 'textcat'))

for source_path in source_paths:
    logger.info('Processing {}...'.format(source_path))
    stream = create_source_stream(source_path, 'en')
    file_counter = 0
    places = []
    for filename, text, _ in stream:
        file_counter += 1
        doc = nlp(text)
        places.extend(list(get_doc_places(doc)))
        if file_counter % 100 == 0:
            logger.info('Processed {} files...{} places found...'.format(file_counter, len(places)))
            #break
        doc = None

df = pd.DataFrame(places, columns=['text', 'lemma', 'lemma*', 'ent_type'])
df_grouped = df.groupby(['lemma*', 'ent_type']).size().reset_index()

df_grouped.to_csv('./NER_source_text_without_tagging_total.txt', sep='\t')


#[z for z in textacy.extract.entities(doc)]
#[[ ent for ent in textacy.extract.entities(doc) ] for doc in corpus if len(doc.ents or []) > 0 ]
