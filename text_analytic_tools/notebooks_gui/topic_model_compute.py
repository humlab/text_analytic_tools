import ipywidgets
import pandas as pd
import text_analytic_tools.utility as utility
import text_analytic_tools.text_analysis.topic_model as topic_model

logger = utility.getLogger('corpus_text_analysis')

def compute_topic_model(data_folder, method, terms, document_index, vectorizer_args, topic_modeller_args, n_topic_window=0):

    result = None

    try:

        n_topics = topic_modeller_args['n_topics']
        apply_idf = vectorizer_args['apply_idf']

        window_coherences = [ ]

        for x_topics in range(max(n_topics - n_topic_window, 2), n_topics + n_topic_window + 1):

            topic_modeller_args['n_topics'] = x_topics

            logger.info('Computing model with {} topics...'.format(x_topics))

            data = topic_model.compute(
                ### corpus=corpus,
                terms=terms,
                documents=document_index,
                ### tick=tick,
                method=method,
                vec_args=vectorizer_args,
                ### tokenizer_args=tokenizer_args,
                tm_args=topic_modeller_args,
                tfidf_weiging=apply_idf
            )

            if x_topics == n_topics:
                result = data

            p_score = data.perplexity_score
            c_score = data.coherence_score
            logger.info('#topics: {}, coherence_score {} perplexity {}'.format(x_topics, c_score, p_score))

            if n_topic_window > 0:
                window_coherences.append({'n_topics': x_topics, 'perplexity_score': p_score, 'coherence_score': c_score})

        if n_topic_window > 0:
            #df = pd.DataFrame(window_coherences)
            #df['n_topics'] = df.n_topics.astype(int)
            #df = df.set_index('n_topics')
            #model_result.coherence_scores = df
            result.coherence_scores = pd.DataFrame(window_coherences).set_index('n_topics')

            #df.to_excel(utility.path_add_timestamp('perplexity.xlsx'))
            #df['perplexity_score'].plot.line()

    except Exception as ex:
        logger.error(ex)
        raise
    finally:
        return result
