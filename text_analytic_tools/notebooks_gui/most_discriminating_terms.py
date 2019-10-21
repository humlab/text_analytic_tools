
import logging
import spacy
import textacy
import textacy.keyterms
import pandas as pd

import text_analytic_tools.utility as utility

logger = logging.getLogger(__name__)

generate_group_filters = utility.widgets.generate_field_filters

def compute_most_discriminating_terms(
    documents,
    corpus,
    group1_filters=None,
    group2_filters=None,
    top_n_terms=25,
    max_n_terms=1000,
    include_pos=None,
    normalize=spacy.attrs.LEMMA
):
    def get_token_attr(token, feature):
        if feature == spacy.attrs.LEMMA:
            return token.lemma_
        if feature == spacy.attrs.LOWER:
            return token.lower_
        return token.orth_

    def get_term_list(corpus, documents, filters):
        docs = utility.get_documents_by_field_filters(corpus, documents, filters)
        return [[ get_token_attr(x, normalize) for x in doc if x.pos_ in include_pos and len(x) > 1 ] for doc in docs]

    docs1 = get_term_list(corpus, documents, group1_filters)
    docs2 = get_term_list(corpus, documents, group2_filters)

    if len(docs1) == 0 or len(docs2) == 0:
        return None

    docs = docs1 + docs2

    in_group1 = [True] * len(docs1) + [False] * len(docs2)

    terms = textacy.keyterms.most_discriminating_terms(docs, in_group1, top_n_terms=top_n_terms, max_n_terms=max_n_terms)
    min_terms = min(len(terms[0]), len(terms[1]))
    df = pd.DataFrame({'Group 1': terms[0][:min_terms], 'Group 2': terms[1][:min_terms] })

    return df
