
import os
import ipywidgets
import textacy
import pandas as pd

import text_analytic_tools.utility as utility
import text_analytic_tools.common.textacy_utility as textacy_utility
import text_analytic_tools.common.text_corpus as text_corpus

import text_analytic_tools.domain.tCoIR.treaty_repository as treaty_repository
import text_analytic_tools.domain.tCoIR.config as config

extend = utility.extend

root_folder = utility.find_parent_folder('text_analytic_tools')

DATA_FOLDER = os.path.join(root_folder, 'data/tCoIR')

print('Data folder: {}'.format(DATA_FOLDER))

CORPUS_NAME_PATTERN = 'tCoIR_*.txt.zip'
CORPUS_TEXT_FILES_PATTERN = '*.txt'

WTI_INDEX_FOLDER = os.path.join(DATA_FOLDER, 'wti_index')

DOCUMENT_FILTERS = [
#         {
#             'type': 'multiselect',
#             'description': 'Party #1',
#             'field': 'party1'
#             # FIXME: Not implemented:
#             # 'filter_query': '(party1=={0}) | (party2=={0})'
#         },
#         {
#             'type': 'multiselect',
#             'description': 'Party #2',
#             'field': 'party2'
#             # FIXME: Not implemented:
#             # 'filter_query': '(party1=={0}) | (party2=={0})'
#         },
#         {
#             'type': 'multiselect',
#             'description': 'Topic',
#             'field': 'topic'
#         },
#         {
#             'type': 'multiselect',
#             'description': 'Year',
#             'field': 'signed_year',
#             'query': 'signed_year > 0'
#         }
]


GROUP_BY_OPTIONS = [
    ('Year', ['signed_year']),
    ('Party1', ['party1']),
    ('Party1, Year', ['party1', 'signed_year']),
    ('Party2, Year', ['party2', 'signed_year']),
    ('Group1, Year', ['group1', 'signed_year']),
    ('Group2, Year', ['group2', 'signed_year']),
]
    #group_by_options = { 'Year': 'year', 'Pope': 'pope', 'Genre': 'genre' } #TREATY_TIME_GROUPINGS[k]['title']: k for k in TREATY_TIME_GROUPINGS }

WTI_INDEX = None

def get_wti_index():
    global WTI_INDEX
    if WTI_INDEX is None:
        WTI_INDEX = treaty_repository.load_wti_index(WTI_INDEX_FOLDER)
    return WTI_INDEX

def get_parties():
    parties = get_wti_index().get_parties()
    return parties

def get_treaties(lang='en', period_group='years_1945-1972'): # , treaty_filter='is_cultural', parties=None)

    columns = [ 'party1', 'party2', 'topic', 'topic1', 'signed_year']
    treaties = get_wti_index().get_treaties(language=lang, period_group=period_group)[columns]

    group_map = get_parties()['group_name'].to_dict()
    treaties['group1'] = treaties['party1'].map(group_map)
    treaties['group2'] = treaties['party2'].map(group_map)

    return treaties

def get_extended_treaties(lang='en'):
    treaties = get_treaties(lang=lang)
    return treaties

def get_corpus_documents(corpus):
    metadata = [ utility.extend({}, doc._.meta, textacy_utility.get_pos_statistics(doc)) for doc in corpus ]
    df = pd.DataFrame(metadata)[['treaty_id', 'filename', 'signed_year', 'party1', 'party2', 'topic1', 'is_cultural'] + textacy_utility.POS_NAMES]
    df['title'] = df.treaty_id
    df['lang'] = df.filename.str.extract(r'\w{4,6}\_(\w\w)')
    df['words'] = df[textacy_utility.POS_NAMES].apply(sum, axis=1)
    return df

def get_region_document_index(source_path, region_name, closed_region, pattern='*.txt'):

    region_country_map = {
        region: party for (region, party) in get_wti_index().get_party_preset_options()
    }

    assert region_name in region_country_map

    filenames = text_corpus.list_archive_files(source_path, pattern)
    documents = compile_documents_by_filename(filenames)

    region_countries = region_country_map[region_name]

    if closed_region:
         region_documents = documents[(documents.party1.isin(region_countries)) & (documents.party2.isin(region_countries))]
    else:
         region_documents = documents[(documents.party1.isin(region_countries)) | (documents.party2.isin(region_countries))]

    return region_documents

def get_treaty_dropdown_options(wti_index, corpus):

    def format_treaty_name(x):

        return '{}: {} {} {} {}'.format(x.name, x['signed_year'], x['topic'], x['party1'], x['party2'])

    documents = wti_index.treaties.loc[get_corpus_documents(corpus).treaty_id]

    options = [ (v, k) for k, v in documents.apply(format_treaty_name, axis=1).to_dict().items() ]
    options = sorted(options, key=lambda x: x[0])

    return options

def get_document_stream(source, lang, document_index=None, id_extractor=None):

    id_extractor = lambda filename: filename.split('_')[0]

    document_index = get_treaties()

    if isinstance(source, str):
        reader = text_corpus.CompressedFileReader(source)
    else:
        reader = source

    id_map = { }

    if 'document_id' not in document_index.columns:
        document_index['document_id'] = document_index.index

    id_map = {
        filename : id_extractor(filename) for filename in reader.filenames
    }

    columns = ['signed_year', 'party1', 'party2']
    df = document_index[columns]
    for filename, text in reader:
        document_id = id_map.get(filename, None)
        metadata = df.loc[document_id].to_dict()
        metadata['filename'] = filename
        metadata['document_id'] = document_id
        metadata['treaty_id'] = document_id
        yield filename, document_id, text, metadata

def compile_documents_by_filename(filenames):

    treaties = get_treaties()
    treaty_map = {
        treaty_id: filename for (treaty_id, filename) in map(lambda x: (x.split('_')[0], x), filenames)
    }
    treaties = treaties[treaties.index.isin(treaty_map.keys())]
    treaties.index.rename('index',inplace=True)
    treaties['document_id'] = treaties.index
    treaties['treaty_id'] = treaties.index
    treaties['local_number'] = treaties.index
    treaties['year'] = treaties.signed_year
    treaties['filename'] = treaties.treaty_id.apply(lambda x: treaty_map[x])

    return treaties

def compile_documents(corpus, corpus_index=None):

    if len(corpus) == 0:
        return None

    if isinstance(corpus, textacy.corpus.Corpus):
        filenames = [ doc._.meta['filename'] for doc in corpus]
    else:
        filenames = corpus.filenames

    df = compile_documents_by_filename(filenames)

    return df

# FIXME VARYING ASPECTs: What attributes to extend
def add_domain_attributes(df, document_index):

    treaties = get_treaties()
    group_map = get_parties()['group_name'].to_dict()

    df_extended = pd.merge(df, treaties, left_index=True, right_index=True, how='inner')
    return df_extended

def load_corpus_index(source_name):
    return None

def treaty_filter_widget(**kwopts):
    default_opts = dict(
        options=config.TREATY_FILTER_OPTIONS,
        description='Topic filter:',
        button_style='',
        tooltips=config.TREATY_FILTER_TOOLTIPS,
        value='is_cultural',
        layout=ipywidgets.Layout(width='200px')
    )
    return ipywidgets.ToggleButtons(**extend(default_opts, kwopts))

def party_name_widget(**kwopts):
    default_opts = dict(
        options=config.PARTY_NAME_OPTIONS,
        value='party_name',
        description='Name',
        layout=ipywidgets.Layout(width='200px')
    )
    return ipywidgets.Dropdown(**extend(default_opts, kwopts))

def parties_widget(**kwopts):
    default_opts = dict(
        options=[],
        value=None,
        rows=12,
        description='Parties',
        disabled=False,
        layout=ipywidgets.Layout(width='180px')
    )
    return ipywidgets.SelectMultiple(**extend(default_opts, kwopts))

def topic_groups_widget(**kwopts):
    default_opts = dict(
        options=config.TOPIC_GROUP_MAPS.keys(),
        description='Category:',
        value='7CORR',
        layout=ipywidgets.Layout(width='200px')
    )
    return ipywidgets.Dropdown(**extend(default_opts, kwopts))

def topic_groups_widget2(**kwopts):
    default_opts = dict(
        options=config.TOPIC_GROUP_MAPS,
        value=config.TOPIC_GROUP_MAPS['7CORR'],
        description='Category:',
        layout=ipywidgets.Layout(width='200px')
    )
    return ipywidgets.Dropdown(**extend(default_opts, kwopts))

def period_group_widget(index_as_value=False, **kwopts):
    default_opts = dict(
        options={
            x['title']: i if index_as_value else x for i, x in enumerate(config.DEFAULT_PERIOD_GROUPS)
        },
        value=len(config.DEFAULT_PERIOD_GROUPS) - 1 if index_as_value else config.DEFAULT_PERIOD_GROUPS[-1],
        description='Divisions',
        layout=ipywidgets.Layout(width='200px')
    )
    return ipywidgets.Dropdown(**extend(default_opts, kwopts))
