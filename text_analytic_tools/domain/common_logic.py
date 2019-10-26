
import os

import pandas as pd

import text_analytic_tools.domain_config as domain_config
import text_analytic_tools.utility as utility
import text_analytic_tools.common.textacy_utility as textacy_utility

current_domain = domain_config.current_domain

logger = utility.getLogger('corpus_text_analysis')

current_domain.SUBSTITUTION_FILENAME = os.path.join(current_domain.DATA_FOLDER, 'term_substitutions.txt')

def get_tagset():
    filepath = os.path.join(current_domain.DATA_FOLDER, 'tagset.csv')
    if os.path.isfile(filepath):
        return pd.read_csv(filepath, sep='\t').fillna('')
    return None

def pos_tags():
    df_tagset = pd.read_csv(os.path.join(current_domain.DATA_FOLDER, 'tagset.csv'), sep='\t').fillna('')
    return df_tagset.groupby(['POS'])['DESCRIPTION'].apply(list).apply(lambda x: ', '.join(x[:1])).to_dict()

def term_substitutions(corpus):
    filename = os.path.join(current_domain.DATA_FOLDER, 'term_substitutions.txt')
    logger.info('Loading term substitution mappings...')
    data = textacy_utility.load_term_substitutions(filename, default_term='_masked_', delim=';', vocab=corpus.spacy_lang.vocab)
    return data

def document_index(corpus):
    try:
        return current_domain.compile_documents(corpus)
    except:
        filenames = [ doc._.meta['filename'] for doc in corpus ]
        return current_domain.compile_documents_by_filename(filenames)