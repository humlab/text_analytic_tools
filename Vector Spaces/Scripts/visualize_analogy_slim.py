# -*- coding: utf-8 -*-
import os
from gensim.models import Word2Vec
from matplotlib import pyplot
import pandas as pd
import numpy as np
from scipy import spatial

# %%

def read_excel(filename, sheet):
    if not os.path.isfile(filename):
        raise Exception("File {0} does not exist!".format(filename))
    with pd.ExcelFile(filename) as xls:
        return pd.read_excel(xls, sheet)

def save_excel(data, filename):
    with pd.ExcelWriter(filename) as writer:
        for (df, name) in data:
            df.to_excel(writer, name)
        writer.save()

def load_model_vector(filename):
    model = Word2Vec.load(filename)
    word_vectors = model.wv
    del model
    return word_vectors

def compute_similarity_to_anthologies(word_vectors, scale_x_pair, scale_y_pair, word_list):

    scale_x = word_vectors[scale_x_pair[0]] - word_vectors[scale_x_pair[1]]
    scale_y = word_vectors[scale_y_pair[0]] - word_vectors[scale_y_pair[1]]

    word_x_similarity = [1 - spatial.distance.cosine(scale_x, word_vectors[x]) for x in word_list ]
    word_y_similarity = [1 - spatial.distance.cosine(scale_y, word_vectors[x]) for x in word_list ]

    df = pd.DataFrame({ 'word': word_list, 'x': word_x_similarity, 'y': word_y_similarity })

    return df

def compute_similarity_to_single_words(word_vectors, word_x, word_y, word_list):

    word_x_similarity = [ word_vectors.similarity(x, word_x) for x in word_list ]
    word_y_similarity = [ word_vectors.similarity(x, word_y) for x in word_list ]

    df = pd.DataFrame({ 'word': word_list, 'x': word_x_similarity, 'y': word_y_similarity })

    return df

# %%

def plot_df(df,xlabel=None,ylabel=None):
    fig = pyplot.figure()
    #pyplot.plot([0,0.75], [0,0.75])
    if not xlabel is None: pyplot.xlabel(xlabel)
    if not ylabel is None: pyplot.ylabel(ylabel)
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(df['x'], df['y'],marker='o')
    for i, txt in enumerate(df['word']):
        ax.annotate(txt, xy=(df['x'].iloc[i], df['y'].iloc[i])) #, textcoords = 'offset points', ha = 'left', va = 'top', **TEXT_KW)
    # pyplot.show()
    pyplot.savefig("plot.png")


def seed_word_toplist(word_vectors, seed_word, topn=100):
     return [ seed_word ] + [ z[0] for z in word_vectors.most_similar_cosmul(seed_word, topn=topn) ]

# %%

if __name__ == "__main__":

    # Load W2V model (created by compute_word2vec script)
    filename = '../data/output/w2v_model_skip_gram_win_5_dim_100_iter_20_mc_5_benedict-xvi.dat'
    word_vectors = load_model_vector(filename)

    # Remove words not found in W2V model vocabulary
    df_toplist = read_excel("../relevant_words.xlsx", "toplist1")
    word_list = list(df_toplist.words.values)

    # Remove words not found in W2V model vocabulary
    word_list = [ x for x in word_list if x in word_vectors.vocab.keys() ]

    # Plot similarity
    #df = compute_similarity_to_single_words(word_vectors, 'north', 'south', word_list)
    #plot_df(df,'<--- West --->', '<--- East --->')
    seed_top_list = seed_word_toplist(word_vectors, 'sweden', 25)

    df_scale = compute_similarity_to_anthologies(word_vectors, ('good', 'evil'), ('heaven', 'hell'), word_list)
    plot_df(df_scale, 'Evil ---- Good', 'Hell ---- Heaven')


    df_w = compute_similarity_to_single_words(word_vectors, 'europe', 'africa', word_list)
    plot_df(df_w, 'europe', 'africa')
