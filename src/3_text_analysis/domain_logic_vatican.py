import pandas as pd
import text_corpus

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

def compile_documents(corpus):
    
    filenames = [ x.metadata['filename'] for x in corpus ]
    
    df = compile_documents_by_filename(filenames)
    
    return df

def get_document_stream(source, lang, **kwargs):

    id_map = { }
    
    if isinstance(source, str):
        # FIXME Use "smart_open" or "open_sesame" library instead 
        reader = text_corpus.CompressedFileReader(source, lang)
    else:
        reader = source
        
    lookup = compile_documents_by_filename(reader.filenames).set_index('filename')
    lookup['filename'] = lookup.index
    
    row_id = 0
    for filename, text in reader:
        metadata = lookup.loc[filename].to_dict()
        yield filename, text, metadata
        row_id += 1
