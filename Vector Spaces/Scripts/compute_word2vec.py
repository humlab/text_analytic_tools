import gzip, shutil
import os, sys
from nltk.tokenize import sent_tokenize, word_tokenize
import gensim.models
from gensim.models.word2vec import Word2Vec
from nltk.corpus import stopwords

if '__file__' in globals():
    sys.path.append(os.path.abspath(__file__))
else:
    sys.path.append('.')

from w2v_projector import W2V_TensorFlow
import zipfile
import glob

# %%
class CorpusCleanser(object):

    def __init__(self, options, language='english'):
        self.stopwords = set(stopwords.words(language))
        self.options = options

    def cleanse(self, sentence, min_word_size = 2):

        sentence = [ x.lower() for x in sentence ]
        #sentence = [ x for x in sentence if len(x) >= min_word_size ]
        if options.get('filter_stopwords', False):
            sentence = [ x for x in sentence if x not in self.stopwords ]
        #sentence = [ x for x in sentence if not x.isdigit() ]
        sentence = [ x for x in sentence if any(map(lambda x: x.isalpha(), x)) ]
        return sentence

    def compress(self, filename):
        with open(filename, 'rb') as f_in:
            with gzip.open(filename + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

# %%

class Word2Vectorizer(object):

    def __init__(self, options):
        self.options = options

    def process(self, sentences):

        model = Word2Vec(sentences,
                         size=self.options['size'],
                         window=self.options['window'],
                         sg=self.options['sg'],
                         iter=self.options['iter'],
                         min_count=self.options['min_count'],
                         workers=self.options['workers'])
        return model

# %%

class ZipFileSentenizer(object):

    def __init__(self, pattern, cleanser=None, extensions = [ 'txt' ]):

        self.pattern = pattern
        self.cleanser = cleanser
        self.extensions = extensions

    def __iter__(self):

        for zip_path in glob.glob(self.pattern):
            with zipfile.ZipFile(zip_path) as zip_file:
                filenames = [ name for name in zip_file.namelist() if any(map(lambda x:  name.endswith(x), self.extensions)) ]
                print(filenames)
                for filename in filenames:
                    with zip_file.open(filename) as text_file:
                        content = text_file.read().decode('utf8')
                        content = content.replace('-\r\n','')
                        content = content.replace('-\n','')
                        if content == '': continue
                        # fix hyphenations i.e. hypens at end om libe
                        for sentence in sent_tokenize(content, language='swedish'):
                            tokens = word_tokenize(sentence)
                            if not self.cleanser is None:
                                tokens = self.cleanser.cleanse(tokens)
                            if len(tokens) > 0:
                                yield tokens

# %% https://github.com/maciejkula/glove-python/issues/42
#import glove
#sentences = ZipFileSentenizer('../data/input/daedalus-segmenterad.zip')
##sentences = [['hej', 'du', 'glade']]
#corpus = glove.Corpus()
#corpus.fit(sentences, window=10)
#g = glove.Glove(no_components=100, learning_rate=0.05)
#g.fit(corpus.matrix, epochs=30, no_threads=4, verbose=True)

# %%
def create_filename(options):
    return 'w2v_model_{}_win_{}_dim_{}_iter_{}_mc_{}{}{}{}'.format(
            'cbow' if options['sg'] == 0 else 'skip_gram',
            options.get('window', 5),
            options.get('size', 100),
            options.get('iter', 5),
            options.get('min_count', 0),
            options.get('id',''),
            '_no_stopwords' if options.get('filter_stopwords') else '',
            '_bigrams' if options.get('bigram_transformer') else '') + '.dat'

if __name__ == "__main__":


    options_list = [
        { 'skip': False, 'id': '_benedict-xvi', 'input_path': '../data/input/benedict-xvi_text.zip', 'output_path': '../data/output', 'window': 5, 'sg': 1, 'size': 100, 'min_count': 5, 'iter': 20, 'workers': 10, 'filter_stopwords': False, 'bigram_transformer': False },
    ]

    for options in options_list:

        if options['skip']: continue

        sentences = ZipFileSentenizer(options['input_path'], CorpusCleanser(options))

        #for x in sentences: print(x)

        if options.get('bigram_transformer', False):
            bigram_transformer = gensim.models.phrases.Phraser(sentences)
            sentences_iterator =  bigram_transformer[sentences]
        else:
            sentences_iterator =  sentences

        model = Word2Vectorizer(options).process(sentences_iterator)

        output_path = os.path.join(options['output_path'], create_filename(options))
        model.save(output_path)
        W2V_TensorFlow().convert_file(output_path, dimension=options['size'])
