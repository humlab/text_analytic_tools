import time
import text_analytic_tools.text_analysis.co_occurrence as co_occurrence
import text_analytic_tools.common.text_corpus as text_corpus
import text_analytic_tools
import text_analytic_tools.utility as utility

logger = utility.getLogger('tCoIR')

current_domain = text_analytic_tools.CURRENT_DOMAIN

region_names = [
    'AFRICA',
    'ASIA',
    'EUROPA',
    'Germany (all)',
    'NORTH AMERICA',
    'OCEANIA',
    'PartyOf5',
    'SOUTH AMERICA',
    'WTI:Arab',
    'WTI:Asian',
    'WTI:Commonwealth',
    'WTI:Communist',
    'WTI:Latin America',
    'WTI:Multiple Parties',
    'WTI:United States of America',
    'WTI:Western Europe'
]

def store_result(data, target_filename):
    try:
        data.to_excel(target_filename)
    except ValueError as ex:
        logger.error(ex)
        logger.info('Storng data as CSV (tab) instead')
        target_filename = target_filename[:-4] + 'tsv'
        data.to_csv(target_filename, sep='\t')

def compute_source_files(source_files):
    for source_file, tag in source_files:
        method = 'HAL'
        corpus = text_corpus.SimplePreparedTextCorpus(source_file, lowercase=True)
        document_index = current_domain.compile_documents(corpus)
        for window_size in [5, 10, 20]:
            result_filename = 'CO_tCoIR_en_45-72.{}_{}_{}_{}.xlsx'.format(time.strftime("%Y%m%d_%H%M"), method, window_size, tag)
            print('Result filename: {}'.format(result_filename))
            df = co_occurrence.compute(corpus, document_index, window_size=window_size, distance_metric=0, normalize='size', method=method)
            store_result(df, result_filename)

def compute_source_files_by_region_filter(source_files):

    for source_file, tag, region_name, closed_region in source_files:
        method = 'HAL'
        document_index = current_domain.get_region_document_index(source_file, region_name=region_name, closed_region=closed_region)
        filenames = document_index.filename.tolist()
        corpus = text_corpus.SimplePreparedTextCorpus(source_file, lowercase=True, itemfilter=filenames)
        document_index = current_domain.compile_documents(corpus)
        for window_size in [20]:
            tag = '{}_{}_{}'.format(tag, region_name.lower().replace(':','_').replace(' ', '_'), 'closed' if closed_region else 'open')
            result_filename = 'CO_tCoIR_en_45-72.{}_{}_{}_{}.xlsx'.format(time.strftime("%Y%m%d"), method, window_size, tag)
            print('Result filename: {}'.format(result_filename))
            df = co_occurrence.compute(corpus, document_index, window_size=window_size, distance_metric=0, normalize='size', method=method)
            store_result(df, result_filename)

# RUN FOR ENTTIRE CORPUS

entire_corpus_source_files = [
    ('data/tCoIR/tCoIR_en_45-72.txt_preprocessed_20191028.lemma.ADJ.NOUN.tokenized.zip', 'lemma.ADJ.NOUN'),
    ('data/tCoIR/tCoIR_en_45-72.txt_preprocessed_20191028.lemma.ADJ.NOUN.VERB.tokenized.zip', 'lemma.ADJ.NOUN.VERB'),
    ('data/tCoIR/tCoIR_en_45-72.txt_preprocessed_20191028.lemma.N.O.U.N.tokenized.zip', 'lemma.NOUN'),
    ('data/tCoIR/tCoIR_en_45-72.txt_preprocessed_20191028.lemma.V.E.R.B.tokenized.zip', 'lemma.VERB')
]
compute_source_files(entire_corpus_source_files)

# RUN FOR SPECIFIC REGIONS:

region_source_files = [
    ('data/tCoIR/tCoIR_en_45-72.txt_preprocessed_20191028.lemma.ADJ.NOUN.VERB.tokenized.zip', 'lemma.ADJ.NOUN.VERB', 'WTI:Communist', False),
    ('data/tCoIR/tCoIR_en_45-72.txt_preprocessed_20191028.lemma.ADJ.NOUN.VERB.tokenized.zip', 'lemma.ADJ.NOUN.VERB', 'WTI:Communist', True),
    ('data/tCoIR/tCoIR_en_45-72.txt_preprocessed_20191028.lemma.ADJ.NOUN.VERB.tokenized.zip', 'lemma.ADJ.NOUN.VERB', 'WTI:Western Europe', False),
    ('data/tCoIR/tCoIR_en_45-72.txt_preprocessed_20191028.lemma.ADJ.NOUN.VERB.tokenized.zip', 'lemma.ADJ.NOUN.VERB', 'WTI:Western Europe', True)
]
compute_source_files_by_region_filter(region_source_files)

print('Done!')