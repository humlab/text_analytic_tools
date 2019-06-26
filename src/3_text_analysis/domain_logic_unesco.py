import os
import pandas as pd
import text_corpus
import re
import logging
import numpy as np

DATA_FOLDER = '../../data/UNESCO'

logger = logging.getLogger('UNESCO')
logger.setLevel(logging.INFO)

CORPUS_NAME_PATTERN = 'unesco_*.txt.zip' 
CORPUS_TEXT_FILES_PATTERN = '*.txt'

DOCUMENT_FILTERS = [
        {
            'type': 'multiselect',
            'description': 'Year',
            'field': 'year',
            'query': 'year > 0'
        }
    ]
        
GROUP_BY_OPTIONS = [
    ('Year', ['year']),
]

FILE_PATTERN = r'([0-9]+)(\w{2})\w*\.txt'

def split_name(filename):
    m = re.match(FILE_PATTERN, filename)
    if m is None:
        logger.error('Parse failed for filename: ' + filename)
        return None, None
    g = m.groups()
    return g[0], g[1]

def compile_documents_by_filename(filenames):

    local_numbers, langs = list(zip(*[ split_name(x) for x in filenames ]))

    df = pd.DataFrame( {
        'local_number': [ int(x) for x in local_numbers],
        'document_id': [ int(x) for x in local_numbers],
        'filename': filenames,
        'lang': langs,
        'year': 0
    })
    #df = df.set_index('local_number')
    
    df['title'] = df.local_number.apply(lambda x: str(x).zfill(10))
    
    return df

def chunk_text(text, step=50000):
    for segment in ( text[i:i + step] for i in range(0,len(text), step) ):
        yield segment

def load_corpus_index(corpus_name):
    '''Given a corpus filename "xxxxx.zip", the document index name is expected to be "xxxxx_index.txt"'''

    def index_filename(corpus_name):
        try:
            m = re.match('(.*)\.txt.*\.zip', corpus_name)
            return m.groups()[0] + '_stats.txt'
        except:
            return None
        
    corpus_index_name = index_filename(corpus_name)
    
    if corpus_index_name is None or not (os.path.isfile(corpus_index_name)):
        logger.info('Corpus index not found (looked for {})'.format(corpus_index_name))
        return None
    
    logger.info('Using corpus index: {}'.format(corpus_index_name))
    
    df = pd.read_csv(corpus_index_name, sep='\t')
    
    df['local_number'] = df.local_number.astype(np.int64)
    df = df.set_index('local_number')
    df['local_number'] = df.index
    df['document_id'] = df.index
    
    return df

def compile_unesco_corpus_index(source):

    df = None
    if hasattr(source, 'path') or isinstance(source, str):
        # Try to load pre-compiled index if exists
        source_path = source.path if hasattr(source, 'path') else source
        df = load_corpus_index(source_path)
        if df is not None:
#             df['local_number'] = df.local_number.astype(np.int64)
#             df = df.set_index('local_number')
#             df['local_number'] = df.index
#             df['document_id'] = df.index
            return df

    if hasattr(source, 'filenames'):
        # Fallback, cretae index out of file names
        df = compile_documents_by_filename(source.filenames).set_index('local_number')
        df['local_number'] = df.index
        if 'year' not in df.columns:
            df['year'] = 0
        return df
    
    return None

def compile_documents(corpus, corpus_index=None):
    
    if len(corpus) == 0:
        return None
    
    if corpus_index is not None:
        corpus_index = corpus_index[corpus_index.filename.isin(filenames)]
        return corpus_index
    
    df = pd.DataFrame([ x.metadata for x in corpus ])

    #logger.warning('Using simplified index based on filenames! Consider using load_corpus_index or compile_unesco_corpus_index instead.')
    #df = compile_documents_by_filename(filenames)
    
    return df

def get_document_stream(source, lang, **kwargs):

    reader = text_corpus.CompressedFileReader(source) if isinstance(source, str) else source
    
    df_corpus_index = compile_unesco_corpus_index(reader)
    
    #reader.filenames = sorted(list(df_corpus_index[(df_corpus_index.year//10).isin([194, 195, 196, 197, 198])].filename.values))
    
    logger.info('Note! Filter is applied: Only first file for each year.')
    reader.filenames = list(df_corpus_index[df_corpus_index.filename.str.contains('en')].groupby('year')['filename'].min().values)
    
    df_corpus_index = df_corpus_index.loc[df_corpus_index.filename.isin(reader.filenames)].sort_values('filename')
    
    assert len(reader.filenames) == len(df_corpus_index)
    
    n_words_threshold = kwargs.get('n_words_threshold', 10)
    n_bytes_trunc_size = kwargs.get('n_bytes_trunc_size', None)
    
    logger.info('INFO: Files having less than {} words will be skipped'.format(n_words_threshold))
    logger.info('INFO: Files greater than {} bytes will be truncated'.format(n_bytes_trunc_size))
    
    processed_count = 0
    empty_count = 0
    truncated_count = 0
    yielded_count = 0
    
    for filename, text in reader:
        
        processed_count += 1
        
        local_number, lang = split_name(filename)
        local_number = int(local_number)
        
        metadata = df_corpus_index.loc[local_number].to_dict()
        
        if metadata['n_words'] < n_words_threshold:
            #logger.info('WARNING: Skipping empty file {} '.format(filename))
            empty_count += 1
            continue
            
        if metadata['lang'] != 'en':
            logger.info('WARNING: Skipping file (unknown language) {} '.format(filename))
            continue
        
        if n_bytes_trunc_size is not None and metadata['n_bytes'] > n_bytes_trunc_size:
            text = text[:n_bytes_trunc_size]
            truncated_count += 1
            
#        i = 0
#        for segment in chunk_text(text, step=50000):
#            basename = str(local_number).zfill(10) + '_' + str(i).zfill(3)
#            yield filename, text[:100000], metadata
#            i += 1
        
        document_id = yielded_count
        yield filename, document_id, text, metadata
        yielded_count += 1

    logger.info('Corpus read done: {} processed files, {} empty files, {} truncated files, {} files yielded'.format(processed_count, empty_count, truncated_count, yielded_count))
    
# FIXME VARYING ASPECTs: What attributes to extend
def add_domain_attributes(df, document_index):
    df_extended = pd.merge(df, document_index, left_index=True, right_index=True, how='inner')    
    return df_extended[['filename', 'year']]
