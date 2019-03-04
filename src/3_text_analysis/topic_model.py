import types
import textacy
import pandas as pd
import gensim
import os
import common.utility as utility
import textacy_corpus_utility as textacy_utility
import topic_model_utility
import mallet_topic_model
import sttm_topic_model
import numpy as np

TEMP_PATH = './tmp/'

# OBS OBS! https://scikit-learn.org/stable/auto_examples/applications/plot_topics_extraction_with_nmf_lda.html
DEFAULT_VECTORIZE_PARAMS = dict(tf_type='linear', apply_idf=False, idf_type='smooth', norm='l2', min_df=1, max_df=0.95)

# FIXME: Bug somewhere...
def n_gram_detector(doc_iter, n_gram_size=2, min_count=5, threshold=100):
    
    for n_span in range(2, n_gram_size+1):
        print('Applying {}_gram detector'.format(n_span))
        n_grams = gensim.models.Phrases(doc_iter(), min_count=min_count, threshold=threshold)
        ngram_modifier = gensim.models.phrases.Phraser(n_grams)
        ngram_doc_iter = lambda: ( ngram_modifier[doc] for doc in doc_iter() )
        doc_iter = ngram_doc_iter
        
    return doc_iter

default_options = {
    'LSI': {
        'engine': gensim.models.LsiModel,
        'options': {
            'corpus': None, 
            'num_topics':  20,
            'id2word':  None
        }
    }
}

def setup_gensim_algorithms(algorithm, document_index, bow_corpus, id2word, tm_args):
    
    # FIXME VARYING ASPECT: 
    #year_column = 'signed_year'
    year_column = 'year'
    
    if algorithm == 'LSI':
        return {
            'engine': gensim.models.LsiModel,
            'options': {
                'corpus': bow_corpus, 
                'num_topics': tm_args.get('n_topics', 0),
                'id2word': id2word,
                'power_iters': 2,
                'onepass': True
            }
        }
    
    if algorithm == 'LDA':
        return {
            'engine': gensim.models.LdaModel,
            'options': {
                'corpus': bow_corpus, 
                'num_topics':  tm_args.get('n_topics', 20),
                'id2word':  id2word,
                'iterations': tm_args.get('max_iter', 1000),
                'passes': tm_args.get('passes', 40),
                'eval_every': 2,
                'update_every': 1,
                'alpha': 'auto',
                'eta': 'auto', # None
                'decay': 0.1, # 0.5
                
                'chunksize': 10,
                'per_word_topics': True,
                'random_state': 100
                
                #'offset': 1.0,
                #'dtype': np.float64
                #'callbacks': [
                #    gensim.models.callbacks.PerplexityMetric(corpus=corpus, logger='visdom'),
                #    gensim.models.callbacks.ConvergenceMetric(distance='jaccard', num_words=100, logger='shell')
                #]
            }
        }
        
    if algorithm =='HDP':
        return {
            'engine': gensim.models.HdpModel,
            'options': {
                'corpus': bow_corpus, 
                'T':  tm_args.get('n_topics', 0),
                'id2word':  id2word,
                #'iterations': tm_args.get('max_iter', 0),
                #'passes': tm_args.get('passes', 20),
                #'alpha': 'auto'
            }
        }
        
    if algorithm == 'DTM':
        return {
            'engine': gensim.models.LdaSeqModel,
            'options': {
                'corpus': bow_corpus, 
                'num_topics':  tm_args.get('n_topics', 0),
                'id2word':  id2word,
                ### 'time_slice': textacy_utility.count_documents_by_pivot(corpus, year_column),
                'time_slice': textacy_utility.count_documents_in_index_by_pivot(document_index, year_column),
                # 'initialize': 'gensim/own/ldamodel',
                # 'lda_model': model # if initialize='gensim'
                # 'lda_inference_max_iter': tm_args.get('max_iter', 0),
                # 'passes': tm_args.get('passes', 20),
                # 'alpha': 'auto'
            }
        }
    
    if algorithm == 'MALLET-LDA':
        return {
            'engine': mallet_topic_model.MalletTopicModel,
            'options': {
                'corpus': bow_corpus, 
                'id2word':  id2word,
                'default_mallet_home': '/usr/local/share/mallet-2.0.8/',
                
                'num_topics':  tm_args.get('n_topics', 100),
                'iterations': tm_args.get('max_iter', 2000),
                'passes': tm_args.get('passes', 20),
                
                'prefix': TEMP_PATH,
                'workers': 4,
                'optimize_interval': 10,
            }
        }

    if algorithm.startswith('STTM-'):
        sttm = algorithm[5:]
        return {
            'engine': sttm_topic_model.STTMTopicModel,
            'options': {
                'sstm_jar_path': './lib/STTM.jar',
                'model': sttm,
                'corpus': bow_corpus,
                'id2word': id2word,
                'num_topics': tm_args.get('n_topics', 20),
                'iterations': tm_args.get('max_iter', 2000),
                'prefix': TEMP_PATH,
                'name': '{}_model'.format(sttm)
                #'vectors', 'alpha'=0.1, 'beta'=0.01, 'twords'=20,sstep=0
            }
        }
    
    assert False, 'Unknown model!'
    
# FIXME VARYING ASPECTS:
# documents = textacy_utility.tCoIR_get_corpus_documents(corpus)
### def compute(corpus, documents, tick=utility.noop, method='sklearn_lda', vec_args=None, term_args=None, tm_args=None, **args):
def compute(terms, documents, method='sklearn_lda', vec_args=None, tm_args=None, **args):
    
    vec_args = utility.extend({}, DEFAULT_VECTORIZE_PARAMS, vec_args)
    
    ### terms = [ list(doc) for doc in textacy_utility.extract_corpus_terms(corpus, term_args) ]
    ### fx_terms = lambda: terms # [ doc for doc in textacy_utility.extract_corpus_terms(corpus, term_args) ]
    fx_terms = lambda: terms
    
    perplexity_score = None
    coherence_score = None
    vectorizer = None
    doc_topic_matrix = None
    doc_term_matrix = None
    
    if not os.path.exists(TEMP_PATH):
        os.makedirs(TEMP_PATH)        
    
    if method.startswith('sklearn'):
        
        vectorizer = textacy.Vectorizer(**vec_args)
        doc_term_matrix = vectorizer.fit_transform(fx_terms())

        model = textacy.TopicModel(method.split('_')[1], **tm_args)
        model.fit(doc_term_matrix)
        
        doc_topic_matrix = model.transform(doc_term_matrix)
        
        id2word = vectorizer.id_to_term
        bow_corpus = gensim.matutils.Sparse2Corpus(doc_term_matrix, documents_columns=False)
        
        # FIXME!!!
        perplexity_score = None
        coherence_score = None
        
    elif method.startswith('gensim_'):
        
        algorithm_name = method.split('_')[1].upper()
        
        id2word = gensim.corpora.Dictionary(fx_terms())
        bow_corpus = [ id2word.doc2bow(tokens) for tokens in fx_terms() ]
        
        if args.get('tfidf_weiging', False):
            # assert algorithm_name != 'MALLETLDA', 'MALLET training model cannot (currently) use TFIDF weighed corpus'
            tfidf_model = gensim.models.tfidfmodel.TfidfModel(bow_corpus)
            bow_corpus = [ tfidf_model[d] for d in bow_corpus ]
        
        ### algorithms = setup_gensim_algorithms(corpus, bow_corpus, id2word, tm_args)
        algorithm = setup_gensim_algorithms(algorithm_name, documents, bow_corpus, id2word, tm_args)
        
        engine = algorithm['engine']
        engine_options = algorithm['options']
        
        model = engine(**engine_options)
        
        if hasattr(model, 'log_perplexity'):
            perplexity_score = model.log_perplexity(bow_corpus, len(bow_corpus))
        
        try:
            coherence_model_lda =  gensim.models.CoherenceModel(model=model, texts=fx_terms(), dictionary=id2word, coherence='c_v')
            coherence_score = coherence_model_lda.get_coherence()
        except Exception as ex:
            logger.error(ex)
            coherence_score = None
            
    processed = topic_model_utility.compile_metadata(
        model,
        bow_corpus,
        id2word,
        documents,
        vectorizer=vectorizer,
        doc_topic_matrix=doc_topic_matrix,
        n_tokens=200
    )
    
    model_data = types.SimpleNamespace(
        topic_model=model,
        id2term=id2word,
        bow_corpus=bow_corpus,
        doc_term_matrix=doc_term_matrix,
        #doc_topic_matrix=doc_topic_matrix,
        #vectorizer=vectorizer,
        processed=processed,
        perplexity_score=perplexity_score,
        coherence_score=coherence_score,
        ### options=dict(method=method, vec_args=vec_args, term_args=term_args, tm_args=tm_args, **args),
        options=dict(method=method, vec_args=vec_args, tm_args=tm_args, **args),
        coherence_scores=None
    )
    
    return model_data

import pickle

def store_model(data, filename):
    
    data = types.SimpleNamespace(
        topic_model=data.topic_model,
        id2term=data.id2term,
        bow_corpus=data.bow_corpus,
        doc_term_matrix=None, #doc_term_matrix,
        doc_topic_matrix=None, #doc_topic_matrix,
        vectorizer=None, #vectorizer,
        processed=data.processed,
        coherence_scores=data.coherence_scores
    )

    with open(filename, 'wb') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

def load_model(filename):
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data

def compute_topic_proportions(document_topic_weights, doc_length_series):

    '''
    Topic proportions are computed in the same as in LDAvis.

    Computes topic proportions over entire corpus.
    The document topic weight (pivot) matrice is multiplies by the length of each document
      i.e. each weight are multiplies ny the document's length.
    The topic frequency is then computed by summing up all values over each topic
    This value i then normalized by total sum of matrice

    theta matrix: with each row containing the probability distribution
      over topics for a document, with as many rows as there are documents in the
      corpus, and as many columns as there are topics in the model.

    doc_length integer vector containing token count for each document in the corpus

    '''
    # compute counts of tokens across K topics (length-K vector):
    # (this determines the areas of the default topic circles when no term is highlighted)
    # topic.frequency <- colSums(theta * doc.length)
    # topic.proportion <- topic.frequency/sum(topic.frequency)

    theta = pd.pivot_table(
        document_topic_weights,
        values='weight',
        index=['document_id'],
        columns=['topic_id']
    ) #.set_index('document_id')

    theta_mult_doc_length = theta.mul(doc_length_series.words, axis=0)

    topic_frequency = theta_mult_doc_length.sum()
    topic_proportion = topic_frequency / topic_frequency.sum()

    return topic_proportion
    