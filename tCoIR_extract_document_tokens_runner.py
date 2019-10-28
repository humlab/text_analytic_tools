
import text_analytic_tools.domain.common_logic as common_logic

import text_analytic_tools
import text_analytic_tools.utility as utility
import text_analytic_tools.common.textacy_utility as textacy_utility
import text_analytic_tools.common as common

logger = utility.getLogger('tCoIR')

current_domain = text_analytic_tools.CURRENT_DOMAIN
container = None

source_path = '/home/roger/source/text_analytic_tools/data/tCoIR/tCoIR_en_45-72.txt.zip'

if container is None:
    container = textacy_utility.load_or_create(
        source_path=source_path,
        language='en',
        document_index=None,
        merge_entities=False,
        overwrite=False,
        use_compression=True,
        disabled_pipes=tuple(("ner", "parser", "textcat"))
    )

corpus             = container.textacy_corpus
min_freq_stats     = { k: textacy_utility.generate_word_count_score(corpus, k, 10) for k in [ 'lemma', 'lower', 'orth' ] }
max_doc_freq_stats = { k: textacy_utility.generate_word_document_count_score(corpus, k, 75) for k in [ 'lemma', 'lower', 'orth' ] }
document_index     = common_logic.document_index(corpus)
term_substitutions = common_logic.term_substitutions(vocab=None)
fx_docs            = lambda corpus: ((doc._.meta['filename'], doc) for doc in corpus)

default_opts = dict(
    term_substitutions=term_substitutions,
    substitute_terms=True,
    ngrams=[1],
    min_word=1,
    normalize='lemma',
    filter_stops=True,
    filter_punct=True,
    named_entities=False,
    include_pos=('ADJ', 'NOUN'),
    chunk_size=0,
    min_freq=2,
    min_freq_stats=min_freq_stats,                 # Must be specified if min_freq > 1
    max_doc_freq=100,
    max_doc_freq_stats=max_doc_freq_stats          # Must be specified if max_doc_freq < 100
)

run_opts = [
    dict(include_pos=('ADJ', 'NOUN', 'VERB')),
    dict(include_pos=('ADJ', 'NOUN')),
    dict(include_pos=('NOUN')),
    dict(include_pos=('VERB'))
]

for _opts in run_opts:

    opts = utility.extend(default_opts, _opts)

    target_filename = utility.path_add_date(container.prepped_source_path)
    target_filename = utility.path_add_suffix(target_filename, '.' + opts.get('normalize',''))
    target_filename = utility.path_add_suffix(target_filename, '.' + '.'.join(list(opts.get('include_pos',''))))
    target_filename = utility.path_add_suffix(target_filename, '.tokenized')

    tokenized_docs = textacy_utility.extract_document_tokens(fx_docs(corpus), **opts)

    df_summary = common.store_tokenized_corpus_as_archive(tokenized_docs, target_filename)

    logger.info("Done! Result stored in '{}'".format(target_filename))

