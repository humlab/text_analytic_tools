
import gensim, gensim.models
from gensim import corpora
import os

class MalletServiceService(object):

    class TextListDocumentSource(object):

        def __init__(self, dictionary, document_list):

            pass

        def __iter__(self):
            
            for document in document_list:
                yield dictionary.doc2bow(document.lower().split())

    def get_mallet_path(self):

        if not 'MALLET_HOME' in os.environ:
            raise Exception('You need to set MALLET_HOME environment variable first.')
            # MALLET_HOME=C:\usr\mallet-2.0.8
        return os.environ['MALLET_HOME'] + '/bin/mallet'

    def compute(self, document_source, options = { }):
        '''
        documents       List of documents (text blocks)
        options_
        remove_n        Filter out the ‘remove_n’ most frequent tokens that appear in the documents.
        extreme_filter  no_below, no_above, keep_n for filtering out tokens number of documents they appear in
        '''

        mallet_path = self.get_mallet_path()

        # Create a dictionary where the key is the 
        # Note: LDA uses a bag-of-word model, disregarding grammar and token sequence
        self.dictionary = corpora.Dictionary(self.documents, prune_at=options.get('prune_at'))

        if options.get('no_below') or options.get('no_above') or options.get('keep_n'):
            self.dictionary.filter_extremes(no_below=options.get('no_below'), no_above=options.get('no_above'), keep_n=options.get('keep_n'))

        if options.get('remove_n'):
            self.dictionary.filter_n_most_frequent(options.get('remove_n'))
        
        corpus = DocumentSource(dictionary, document_source) # [ dictionary.doc2bow(document) for document in documents ]

        model = gensim.models.wrappers.LdaMallet(
            mallet_path,
            corpus=corpus,
            num_topics=options.get('num_topics', 20),
            id2word=dictionary,
            prefix=options.get('store_prefix') # alpha=50, workers=4, optimize_interval=0, iterations=1000, topic_threshold=0.0 
        )

        return {
            'dictionary': dictionary,
            'corpus': corpus,
            'model': model,
            'options': options
        }
