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

# %%
def word_scale_similarity(word_vectors, scale_x_pair, scale_y_pair, word_list):

    scale_x = word_vectors[scale_x_pair[0]] - word_vectors[scale_x_pair[1]]
    scale_y = word_vectors[scale_y_pair[0]] - word_vectors[scale_y_pair[1]]

    word_x_similarity = [1 - spatial.distance.cosine(scale_x, word_vectors[x]) for x in word_list ]
    word_y_similarity = [1 - spatial.distance.cosine(scale_y, word_vectors[x]) for x in word_list ]

    df = pd.DataFrame({ 'word': word_list, 'x': word_x_similarity, 'y': word_y_similarity })

    return df

# %%

def word_pair_list_similarity(word_vectors, word_x, word_y, word_list):

    word_x_similarity = [ word_vectors.similarity(x, word_x) for x in word_list ]
    word_y_similarity = [ word_vectors.similarity(x, word_y) for x in word_list ]

    df = pd.DataFrame({ 'word': word_list, 'x': word_x_similarity, 'y': word_y_similarity })

    return df

# %%

def word_pair_list_similarity2(word_vectors, word_x, word_y, seed_word, topn=100):


    word_toplist = [ seed_word ] + [ z[0] for z in word_vectors.most_similar_cosmul(seed_word, topn=100) ]

    word_x_similarity = [ word_vectors.similarity(x, word_x) for x in word_toplist ]
    word_y_similarity = [ word_vectors.similarity(x, word_y) for x in word_toplist ]

    df = pd.DataFrame({ 'word': word_toplist, 'x': word_x_similarity, 'y': word_y_similarity })

    return df

# %%

def word_pair_toplist_similarity(word_vectors, word_x, word_y, topn=50):

    word_x_toplist = [ word_x ] + word_vectors.most_similar_cosmul(word_x, topn=topn)
    word_y_toplist = [ word_y ] + word_vectors.most_similar_cosmul(word_y, topn=topn)

    word_toplist = [ x[0] for x in word_x_toplist + word_y_toplist ]

    return word_pair_list_similarity(word_vectors, word_x, word_y, word_toplist)

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
    pyplot.show()

# %%

def generate_plot(words, x_word, y_word, iter=5, topn=3, similar_threshold= 0.5):
    word_list = SimilarWordGenerater(word_vectors).generate(words, iter, topn, [], similar_threshold)
    df = word_pair_list_similarity(word_vectors, x_word, y_word, word_list)
    plot_df(df,'<--- {} --->'.format(x_word), '<--- {} --->'.format(y_word))

# %%
def plot_locations():
    df_swe_loc = pd.read_excel('../data/ner_swe_loc_plc.xlsx', 'swe_loc_plc')
    df_place_minus_one = pd.DataFrame(df_swe_loc.place.apply(lambda x: x[:-1]))
    df_place_minus_one.columns = ['place']
    swe_loc_list = list(pd.merge(df_swe_loc,df_place_minus_one,how='inner',left_on='place',right_on='place')['place'].unique())
    swe_loc_list = [ x for x in swe_loc_list if x in word_vectors.vocab ]
    df = word_pair_list_similarity(word_vectors, 'industri', 'jordbruk',swe_loc_list)
    plot_df(df,'<--- Industri --->', '<--- Jordbruk --->')


# %%

if __file__ == '__main__':

    filename = '../data/output/w2v_model_skip_gram_win_5_dim_100_iter_20_mc_5_benedict-xvi.dat'

    word_vectors = load_model_vector(filename)

    # %%


    df_toplist = read_excel("../relevant_words.xlsx", "toplist1")
    word_list = list(df_toplist.words.values)

    word_list = [ x for x in word_list if x in word_vectors.vocab.keys() ]

    df = word_pair_list_similarity(word_vectors, 'west', 'east', word_list)
    plot_df(df,'<--- West --->', '<--- East --->')


    df = word_pair_list_similarity2(word_vectors, 'north', 'south', 'poor')
    plot_df(df,'North', 'South')
    word_list = SimilarWordGenerater(word_vectors).generate(['kärnkraft'], 5, topn=3)
    df_scale = word_scale_similarity(word_vectors, ('stad', 'landsbygd'), ('jordbruk', 'industri'), word_list)
    plot_df(df_scale, 'Stad ---- Landsbygd', 'jordbruk ---- industri')



