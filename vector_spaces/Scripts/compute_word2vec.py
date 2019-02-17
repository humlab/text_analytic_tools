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

    def __init__(self, pattern, cleanser=None, extensions = [ 'txt' ], genres = None):

        self.pattern = pattern
        self.cleanser = cleanser
        self.extensions = extensions
        self.genres = genres
        self.language = 'english'

    def is_satisfied_by_extension(self, filename):
        return any(map(lambda x:  filename.endswith(x), self.extensions))

    def is_satisfied_by_genre(self, filename):
        return len(self.genres or []) == 0 or any(map(lambda x: x in filename, self.genres))

    def __iter__(self):

        for zip_path in glob.glob(self.pattern):
            with zipfile.ZipFile(zip_path) as zip_file:
                filenames = [
                    filename for filename in zip_file.namelist()
                        if self.is_satisfied_by_extension(filename)
                            and self.is_satisfied_by_genre(filename)
                ]
                # print(filenames)
                for filename in filenames:
                    with zip_file.open(filename) as text_file:
                        content = text_file.read().decode('utf8')
                        content = content.replace('-\r\n','')
                        content = content.replace('-\n','')
                        if content == '': continue
                        # fix hyphenations i.e. hypens at end om libe
                        for sentence in sent_tokenize(content, language=self.language):
                            tokens = word_tokenize(sentence)
                            if not self.cleanser is None:
                                tokens = self.cleanser.cleanse(tokens)
                            if len(tokens) > 0:
                                yield tokens


# %%
def create_filename(options):
    return 'w2v_model_{}_win_{}_dim_{}_iter_{}_mc_{}{}{}{}{}.dat'.format(
            'cbow' if options['sg'] == 0 else 'skip_gram',
            options.get('window', 5),
            options.get('size', 100),
            options.get('iter', 5),
            options.get('min_count', 0),
            options.get('id',''),
            '_no_stopwords' if options.get('filter_stopwords') else '',
            '_bigrams' if options.get('bigram_transformer') else '',
            '_'.join(options.get('genres',[])) if options.get('genres', None) is not None else '')

if __name__ == "__main__":
    '''
    genres = [
        'angelus', # klockringning The Angelus is a Catholic devotion commemorating the Incarnation.
        'audiences',
        'homilies',  # A homily is a commentary that follows a reading of scripture
        'speeches',
        'letters',
        'apost',
        'messages',
        'encyclicals',
        'prayers',
        'travels',
        'motu',
        'bulls',
        'cotidie'
    ]
    '''
    defaults = {
        'skip': False,
        'output_path': '../data/output',
        'window': 5,
        'sg': 1,
        'size': 100,
        'min_count': 5,
        'iter': 20,
        'workers': 10,
        'filter_stopwords': False,
        'bigram_transformer': False,
        'genres': None
    }


#        { 'id': '_benedict-xvi', 'input_path': '../data/input/benedict-xvi_text.zip', 'size': 50, 'genres': ['speeches'] },
#        { 'id': '_francesco', 'input_path': '../data/input/francesco_text.zip', 'size': 50, 'genres': ['speeches'] },
#
#        { 'id': '_benedict-xvi', 'input_path': '../data/input/benedict-xvi_text.zip' },
#        { 'id': '_francesco', 'input_path': '../data/input/francesco_text.zip' },
#
#        { 'id': '_benedict-xvi', 'input_path': '../data/input/benedict-xvi_text.zip', 'genres': ['speeches'] },
#        { 'id': '_francesco', 'input_path': '../data/input/francesco_text.zip', 'genres': ['speeches'] }

#        { 'id': '_benedict-xvi', 'input_path': '../data/input/benedict-xvi_text.zip', 'bigram_transformer': False, 'filter_stopwords': False },
#        { 'id': '_francesco', 'input_path': '../data/input/francesco_text.zip', 'bigram_transformer': False, 'filter_stopwords': False }

    options_list = [

        { 'id': '_benedict-xvi+francesco', 'input_path': '../data/input/benedict-xvi+francesco_text.zip', 'bigram_transformer': False, 'filter_stopwords': False }

    ]

    for opt in options_list:

        options = dict(defaults)
        options.update(opt)

        if options.get('skip', False) is True:
            continue

        sentences = ZipFileSentenizer(options['input_path'], CorpusCleanser(options))

        #for x in sentences: print(x)

        if options.get('bigram_transformer', False):
            bigram_transformer = gensim.models.Phrases(sentences)
            sentences_iterator =  bigram_transformer[sentences]
        else:
            sentences_iterator =  sentences

        model = Word2Vectorizer(options).process(sentences_iterator)

        output_path = os.path.join(options['output_path'], create_filename(options))
        model.save(output_path)

        W2V_TensorFlow().convert_file(output_path, dimension=options['size'])
