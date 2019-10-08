# -*- coding: utf-8 -*-
#from gensim.models.word2vec import Word2Vec
from gensim.models import Word2Vec
from sklearn.decomposition import PCA
from matplotlib import pyplot

filename = '../data/output/w2v_model_skip_gram_win_5_dim_50_iter_20_mc_5_complete_not_segmented.dat'

model = Word2Vec.load(filename)
# %%

print('Top 10 words       : ', model.wv.index2word[0:10])
print('Size of vocabulary : ', len(model.wv.vocab))


# %%
# fit a 2d PCA model to the vectors
X = model[model.wv.vocab]
pca = PCA(n_components=2)
result = pca.fit_transform(X)
# create a scatter plot of the projection of dimensions PC1 and PC2
pyplot.scatter(result[:100, 0], result[:100, 1])
words = list(model.wv.vocab)[0:100]
for i, word in enumerate(words):
	pyplot.annotate(word, xy=(result[i, 0], result[i, 1]))
pyplot.show()

# %%
# farthest away from a word
model.most_similar('polhem',topn=50)
#model.similarity_comul('ond','god')
# %%
# which word is to “x” as “y” is to “z”?
#model.most_similar(positive=['x','y'], negative=['z'])
model.most_similar(positive=['karin','han'], negative=['hon'],topn=20)

# %%
''' Words closest to "karin" (which are essentially all first names) and
pick out the ones which are closer to “he” than to “she”.
'''
[ x[0] for x in model.most_similar('karin',topn=2000)
    if model.similarity(x[0],'han') > model.similarity(x[0], 'hon')]

#print(model.most_similar(positive=['teknik', 'producent'], negative=['teknik']))
#model.most_similar(positive=['flicka', 'pappa'], negative=['pojke'], topn=20)

# CHECK: https://stackoverflow.com/questions/43776572/visualise-word2vec-generated-from-gensim
