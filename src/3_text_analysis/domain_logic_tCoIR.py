
import common.utility as utility
import pandas as pd
import textacy_corpus_utility 
# FIXME VARYING ASPECTS
def tCoIR_get_corpus_documents(corpus):
    
    metadata = [ utility.extend({}, doc.metadata, _get_pos_statistics(doc)) for doc in corpus ]
    df = pd.DataFrame(metadata)[['treaty_id', 'filename', 'signed_year', 'party1', 'party2', 'topic1', 'is_cultural']+POS_NAMES]
    df['title'] = df.treaty_id
    df['lang'] = df.filename.str.extract(r'\w{4,6}\_(\w\w)')  #.apply(lambda x: x.split('_')[1][:2])
    df['words'] = df[POS_NAMES].apply(sum, axis=1)
    return df

def get_treaty_dropdown_options(wti_index, corpus):
    
    def format_treaty_name(x):
        return '{}: {} {} {} {}'.format(x.name, x['signed_year'], x['topic'], x['party1'], x['party2'])
    
    documents = wti_index.treaties.loc[textacy_utility.get_corpus_documents(corpus).treaty_id]

    options = [ (v, k) for k, v in documents.apply(format_treaty_name, axis=1).to_dict().items() ]
    options = sorted(options, key=lambda x: x[0])

    return options

def get_document_stream(corpus_path, lang, document_index=None, id_extractor=None):

    id_extractor = lambda filename: filename.split('_')[0]

    documents = CompressedFileReader(corpus_path, lang)

    id_map = { }
    
    if document_index is not None:
        
        if 'document_id' not in document_index.columns:
            document_index['document_id'] = document_index.index
            
        id_map = {
            filename : id_extractor(filename) for filename in documents.filenames
        }

    for filename, text in documents:
        document_id = id_map.get(filename, None)
        metadata = None if document_index is None else document_index.iloc[document_id].to_dict()
        yield filename, text, document_id, metadata
        
        