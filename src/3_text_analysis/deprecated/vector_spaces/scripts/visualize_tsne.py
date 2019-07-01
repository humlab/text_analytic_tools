# -*- coding: utf-8 -*-
from gensim.models import Word2Vec
from sklearn.manifold import TSNE
from matplotlib import pyplot
import pandas as pd
# %%

filename = '../data/output/w2v_model_cbow_win_5_dim_300_iter_20_mc_10.dat'

def load_model(filename):
    return Word2Vec.load(filename)

# %%
model = load_model(filename)
vocab = list(model.wv.vocab)
X = model[vocab]
tsne = TSNE(n_components=2)
X_tsne = tsne.fit_transform(X)

# %%

def plot_df(df):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(df['x'], df['y'])
    for i, txt in enumerate(df['word']):
        ax.annotate(txt, (df['x'].iloc[i], df['y'].iloc[i]))
    pyplot.show()

# %%

df = pd.concat([pd.DataFrame(X_tsne), pd.Series(vocab)], axis=1)

plot_df(df)
