import pandas as pd
import text_corpus

DATA_FOLDER = '../../data'
CORPUS_NAME_PATTERN = '*.txt.zip'
CORPUS_TEXT_FILES_PATTERN = '*.txt'

DOCUMENT_FILTERS = [
        {
            'type': 'multiselect',
            'description': 'Pope',
            'field': 'pope'
        },
        {
            'type': 'multiselect',
            'description': 'Genre',
            'field': 'genre'
        },
        {
            'type': 'multiselect',
            'description': 'Year',
            'field': 'year',
            'query': 'year > 0'
        }
    ]

POPE_GROUP_FILTERS = [
        {
            'type': 'multiselect',
            'description': 'Pope',
            'field': 'pope'
        },
        {
            'type': 'multiselect',
            'description': 'Genre',
            'field': 'genre'
        },
        {
            'type': 'multiselect',
            'description': 'Year',
            'field': 'year'
        }
    ]

GROUP_BY_OPTIONS = [
    ('Year', ['year']),
    ('Pope', ['pope']),
    ('Pope, Year',  ['pope', 'year']),
    ('Genre', ['genre']),
    ('Pope, genre', ['pope', 'genre']),
    ('Pope, year, genre', ['pope', 'year', 'genre'])
]

def compile_documents_by_filename(filenames):

    parts = [ x.split('_') for x in filenames ]

    pope, lang, genre, year, sub_genre = list(zip(*[ (x[0], x[1], x[2], x[3]if x[3].isdigit() else x[4], x[4] if x[3].isdigit() else x[3])  for x in parts ]))

    df = pd.DataFrame( {
        'filename': filenames,
        'pope': pope,
        'lang': lang,
        'genre': genre,
        'year': [ int(x) for x in year],
        'sub_genre': sub_genre
    })
    df['document_id'] = df.index
    df['title'] = df.filename

    return df

def _compile_documents(corpus, corpus_index=None):

    if len(corpus) == 0:
        return None

    if corpus_index is not None:
        corpus_index = corpus_index[corpus_index.filename.isin(filenames)]
        return corpus_index

    df = pd.DataFrame([ x._.meta for x in corpus ])

    return df

def compile_documents(corpus, index=None):

    filenames = [ x._.meta['filename'] for x in corpus ]

    df = compile_documents_by_filename(filenames)

    return df

def get_document_stream(source, lang, **kwargs):

    id_map = { }

    if isinstance(source, str):
        # FIXME Use "smart_open" or "open_sesame" library instead
        reader = text_corpus.CompressedFileReader(source)
    else:
        reader = source

    lookup = compile_documents_by_filename(reader.filenames).set_index('filename')
    lookup['filename'] = lookup.index

    row_id = 0
    for filename, text in reader:
        metadata = lookup.loc[filename].to_dict()
        yield filename, row_id, text, metadata
        row_id += 1

# FIXME VARYING ASPECTs: What attributes to extend
def add_domain_attributes(df, document_index):
    df_extended = pd.merge(df, document_index, left_index=True, right_index=True, how='inner')
    return df_extended[['filename', 'year', 'genre', 'keyterms']]
