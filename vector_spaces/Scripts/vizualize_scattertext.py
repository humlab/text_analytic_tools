# -*- coding: utf-8 -*-

#import spacy
from gensim.models import word2vec
from scattertext import SampleCorpora, word_similarity_explorer_gensim, Word2VecFromParsedCorpus
from scattertext.CorpusFromParsedDocuments import CorpusFromParsedDocuments

#nlp = spacy.en.English()
#convention_df = SampleCorpora.ConventionData2012.get_data()
#convention_df['parsed'] = convention_df.text.apply(nlp)
#corpus = CorpusFromParsedDocuments(convention_df, category_col='party', parsed_col='parsed').build()

filename = '../data/output/w2v_model_cbow_win_5_dim_300_iter_20_mc_10.dat'

model = word2vec.Word2Vec.load(filename)

html = word_similarity_explorer_gensim(None,
                                       category='democrat',
                                       category_name='Democratic',
                                       not_category_name='Republican',
                                       target_term='jobs',
                                       minimum_term_frequency=5,
                                       pmi_threshold_coefficient=4,
                                       width_in_pixels=1000,
                                       #metadata=convention_df['speaker'],
                                       word2vec=model,
                                       max_p_val=0.05,
                                       save_svg_button=True)


#html = word_similarity_explorer_gensim(corpus,
#                                       category='democrat',
#                                       category_name='Democratic',
#                                       not_category_name='Republican',
#                                       target_term='jobs',
#                                       minimum_term_frequency=5,
#                                       pmi_threshold_coefficient=4,
#                                       width_in_pixels=1000,
#                                       metadata=convention_df['speaker'],
#                                       word2vec=Word2VecFromParsedCorpus(corpus, model).train(),
#                                       max_p_val=0.05,
#                                       save_svg_button=True)

open('./demo_gensim_similarity.html', 'wb').write(html.encode('utf-8'))
