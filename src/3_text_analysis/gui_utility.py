import sys

sys.path = list(set(['.', '..']) - set(sys.path)) + sys.path

import textacy_corpus_utility as textacy_utility
import ipywidgets as widgets
import common.widgets_config as widgets_config
import common.utility as utility

def generate_field_filters(documents, opts):
    filters = []
    for opt in opts:  # if opt['type'] == 'multiselect':
        options =  opt.get('options', list(documents[opt['field']].unique()))
        description = opt.get('description', '')
        rows = min(4, len(options))
        gf = utility.extend(opt, widget=widgets_config.selectmultiple(description, options, value=(), rows=rows))
        filters.append(gf)
    return filters

def get_document_id_by_field_filters(documents, filters):
    df = documents
    for k, v in filters:
        if len(v or []) > 0:
            df = df[df[k].isin(v)]
    return list(df.index)

def get_documents_by_field_filters(corpus, documents, filters):
    ids = get_document_id_by_field_filters(documents, filters)
    docs = ( x for x in corpus if x.metadata['document_id'] in ids)
    return docs
        