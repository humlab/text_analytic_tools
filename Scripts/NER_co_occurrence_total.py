#%%
import os, time
import pandas as pd
import numpy as np
import math
#from sklearn.neighbors.kde import KernelDensity
# %%
class LocationRepository:

    def __init__(self, data_folder):
        self.data_folder = data_folder

    def get_locations(self, popes_ner_filename, popes_wc_filename):
        df = pd.read_excel(os.path.join(self.data_folder, popes_ner_filename), 'Data', dtype={'Concept': 'str'})
        df_wc = pd.read_excel(os.path.join(self.data_folder, popes_wc_filename), 'Data')
        df_wc['document'] = df_wc['document'].apply(lambda x: x[:-4])
        df_plus = pd.merge(df,df_wc,how='inner',left_on='Document',right_on='document')
        df_locations = df_plus.loc[(df_plus.Classifier=='LOCATION')]
        return df_locations

    def ts_data_path(self, filename):
        return os.path.join(self.data_folder, '{}_{}'.format(time.strftime("%Y%m%d%H%M"), filename))

    def store(self, data, filename):
        writer = pd.ExcelWriter(filename)
        for key in data.keys():
            data[key].reset_index().to_excel(writer, key)
        writer.save()

# %%

class TfIdfCooccurrence:

    def compute_location_counts(self, df_locations):

        df_document_location_count = df_locations.groupby(['Document', 'Year', 'Genre', 'Concept', 'WordCount'])[['Count']].sum().reset_index()
        df_document_location_count.columns = ['Document', 'Year', 'Genre', 'Concept', 'WordCount', 'PlaceOccurenceCount']
        df_document_location_count['Count1K'] =  df_document_location_count.PlaceOccurenceCount / (df_document_location_count.WordCount / 1000.0)

        total_number_of_documents = df_locations.size

        df_location_document_counts = df_locations.groupby(['Concept']).Document.nunique()
        df_location_document_counts = pd.DataFrame(df_location_document_counts)
        df_location_document_counts.columns = ['DocumentCount']

        df_number_of_unique_places_per_document = df_locations.groupby(['Document', 'Year', 'Genre'])[['Count']].sum().reset_index()
        df_number_of_unique_places_per_document.columns = ['Document', 'Year', 'Genre', 'PlaceCount']

        df = pd.merge(df_number_of_unique_places_per_document, df_document_location_count, left_on="Document", right_on="Document")[['Document', 'Year_x', 'Concept', 'PlaceOccurenceCount', 'PlaceCount', 'WordCount', 'Count1K']]
        df.columns = ['Document', 'Year', 'Concept', 'PlaceOccurenceCount', 'PlaceCount', 'WordCount', 'Count1K']
        df['TF'] = df['PlaceOccurenceCount'] / df['WordCount']
        df = pd.merge(df, df_location_document_counts, left_on="Concept", right_index=True)
        df['IDF'] = df.DocumentCount.apply(lambda x: math.log(total_number_of_documents * x))
        df['TF_IDF'] = df.TF * df.IDF

        return df

    def compute(self, df_locations):

        df_location_counts = self.compute_location_counts(df_locations)

        df_document_cooccurrence = pd.merge(df_location_counts, df_location_counts, left_on=["Document", "Year"], right_on=["Document", "Year"])[[ 'Document', 'Year', 'Concept_x', 'Concept_y', 'TF_IDF_x', 'TF_IDF_y' ]]
        df_document_cooccurrence = df_document_cooccurrence.loc[(df_document_cooccurrence.Concept_x < df_document_cooccurrence.Concept_y)]
        df_document_cooccurrence['Weight'] = df_document_cooccurrence['TF_IDF_x'] * df_document_cooccurrence['TF_IDF_y']
        # df_document_cooccurrence = df_document_cooccurrence [['Document', 'Year', 'Concept_x', 'Concept_y', 'Weight']]
        df_document_cooccurrence = df_document_cooccurrence.set_index(['Concept_x', 'Concept_y'])
        df_corpus_cooccurrence = df_document_cooccurrence.groupby(['Concept_x', 'Concept_y'])[['Weight']].agg(['count', 'sum', 'mean'])

        return {
                'location_counts': df_location_counts,
                'document_cooccurrence': df_document_cooccurrence,
                'corpus_cooccurrence': df_corpus_cooccurrence.reset_index()
        }

# %%

class PointwiseMutualInformation:

#    def pmi_func1(self, dff, x, y):
#        df = dff.copy()
#        df['f_x'] = df.groupby(x)[x].transform('count')
#        df['f_y'] = df.groupby(y)[y].transform('count')
#        df['f_xy'] = df.groupby([x, y])[x].transform('count')
#        df['pmi'] = np.log(len(df.index) * df['f_xy'] / (df['f_x'] * df['f_y']) )
#        return df
#
#    def pmi_func2(self, df, x, y):
#        freq_x = df.groupby(x).transform('count')
#        freq_y = df.groupby(y).transform('count')
#        freq_x_y = df.groupby([x, y]).transform('count')
#        df['pmi'] = np.log( len(df.index) *  (freq_x_y / (freq_x * freq_y)) )
#
#    # pmi with kernel density estimation
#    def kernel_pmi_func(self, df, x, y):
#        # reshape data
#        x = np.array(df[x])
#        y = np.array(df[y])
#        x_y = np.stack((x, y), axis=-1)
#
#        # kernel density estimation
#        kde_x = KernelDensity(kernel='gaussian', bandwidth=0.1).fit(x[:, np.newaxis])
#        kde_y = KernelDensity(kernel='gaussian', bandwidth=0.1).fit(y[:, np.newaxis])
#        kde_x_y = KernelDensity(kernel='gaussian', bandwidth=0.1).fit(x_y)
#
#        # score
#        p_x = pd.Series(np.exp(kde_x.score_samples(x[:, np.newaxis])))
#        p_y = pd.Series(np.exp(kde_y.score_samples(y[:, np.newaxis])))
#        p_x_y = pd.Series(np.exp(kde_x_y.score_samples(x_y)))
#
#        return np.log( p_x_y / (p_x * p_y) )

    def compute_context_cooccurrence(self, df_locations, split_columns, context_columns):
        df_context = df_locations.groupby(split_columns + context_columns + ['Concept'])[['Count']].sum().reset_index()
        df = pd.merge(df_context, df_context, left_on=split_columns + context_columns, right_on=split_columns + context_columns)[split_columns + context_columns + ['Concept_x', 'Concept_y', 'Count_x', 'Count_y' ]]
        df = df.loc[(df.Concept_x < df.Concept_y)]
        df['CooCount'] = df.Count_x * df.Count_y
        return df

    # PMI(x, y) = log( p(x,y) / p(x) * p(y) )
    def compute(self, df_locations, context_columns, split_columns):

        df_context_cooc = self.compute_context_cooccurrence(df_locations, split_columns, context_columns)

        df_concept_count = df_locations.groupby(split_columns + ['Concept'])['Count'].sum().reset_index()
        df_total_count = df_locations.groupby(split_columns)['Count'].sum().reset_index()

        columns = split_columns + ['Concept_x', 'Concept_y']
        df = df_context_cooc.groupby(columns)['CooCount'].sum().reset_index()
        df.columns = columns = columns + ['f_xy']

        df = pd.merge(df, df_concept_count, left_on=split_columns + ['Concept_x'], right_on=split_columns + ['Concept'], how='inner')[columns + ['Count']]
        df.columns = columns = columns + ['f_x']

        df = pd.merge(df, df_concept_count, left_on=split_columns + ['Concept_y'], right_on=split_columns + ['Concept'], how='inner')[columns + ['Count']]
        df.columns = columns = columns + ['f_y']

        df = pd.merge(df, df_total_count, on=split_columns, how='inner')
        df.columns = columns = columns + ['f_total']

        df['pmi'] = np.log(df['f_total'] * (df['f_xy'] / (df['f_x'] * df['f_y'])) )
        df['ppmi'] = df['pmi'].apply(lambda x: max(x, 0))

        return df

from sklearn.feature_extraction.text import TfidfVectorizer

class TfIdMeanScore:

    def compute(self, df_locations):
        '''
        Computes TF-IDF score and returns mean scores for each concept
        '''
        df = df_locations.groupby(['Document','Concept']).Count.sum().reset_index()
        df['ConceptList'] = df.reset_index().Concept.apply(lambda x: [ x.replace(' ', '_') ]) * df.Count
        df['Concepts'] = df.ConceptList.apply(lambda x: ' '.join(x))
        df = df.groupby('Document').Concepts.agg(lambda x: ' '.join(x))
        v = TfidfVectorizer()
        x = v.fit_transform(df)
        weights = np.asarray(x.mean(axis=0)).ravel().tolist()
        df_weights = pd.DataFrame({'term': v.get_feature_names(), 'weight': weights})

        return df_weights.sort_values(by='weight', ascending=False)


class TfIdYearlyMeanScore:

    def create_corpus(self, df_locations):
        '''
        Creates the 'documents' that are to be used in the TF-IDF vectorization/scoring.
        Parameter df_locations containes the LOC entities identified by Stanford NER,
        and where similar locations have been merged into single concepts.
        We need to repeat each location as many times as they occur in the original document.
        '''
        df = df_locations.groupby(['Year', 'Document','Concept']).Count.sum().reset_index()
        df['ConceptList'] = df.Concept.apply(lambda x: [ x.replace(' ', '_') ]) * df.Count
        df['Concepts'] = df.ConceptList.apply(lambda x: ' '.join(x))
        df_corpus = df.groupby(['Year', 'Document']).Concepts.agg(lambda x: ' '.join(x))
        return df_corpus

    def compute_mean_scores(self, df_corpus, tf, tfidf_matrix):
        '''
        Compiles the result set that contains triplets (year, concept, mean score) for
        each year and concept that exists in the original corpus. The score of a concept
        is computed as the mean score of that concept in all documents for a specific year.
        '''
        df_corpus = df_corpus.reset_index()
        min_year = df_corpus.Year.min()
        max_year = df_corpus.Year.max()
        df_scores = None
        for year in range(min_year, max_year + 1):
            year_indices = df_corpus.loc[(df_corpus.Year == year)].index.tolist()
            year_matrix = tfidf_matrix.tocsr()[year_indices,:]
            year_mean_scores = np.asarray(year_matrix.mean(axis=0)).ravel().tolist()
            df_year_scores = pd.DataFrame({ 'year': year, 'term': tf.get_feature_names(), 'score': year_mean_scores})
            df_scores = df_year_scores if df_scores is None else df_scores.append(df_year_scores, ignore_index=True)
        return df_scores

    def compute(self, df_locations):
        '''
        Main function that computes the TF-IDF mean score
        '''
        df_corpus = self.create_corpus(df_locations)
        tf = TfidfVectorizer(min_df = 0)
        tfidf_matrix = tf.fit_transform(df_corpus)
        mean_scores = self.compute_mean_scores(df_corpus, tf, tfidf_matrix)
        return mean_scores

        #tfidf_score_of_each_feature = dict(zip(tf.get_feature_names(), tf.idf_))
        #feature_names = tf.get_feature_names()
        #dense = tfidf_matrix.todense()
        #doc_id = 0
        #length_first_document = len(dense[doc_id].tolist()[0])
        #document = dict(zip(tf.get_feature_names(), tfidf_matrix[doc_id].todense().tolist()[0]))
        #phrase_scores = [ (x, document[x]) for x in document.keys() if document[x] > 0 ]
        #document = dense[0].tolist()[0]
        #phrase_by_index_scores = [pair for pair in zip(range(0, len(document)), document) if pair[1] > 0]
        #phrase_scores = [ (i, feature_names[i], x) for (i,x) in phrase_by_index_scores ]

# %% PointwiseMutualInformation
def compute_ppmi_ococcurrence(df_locations, popes = [ 'benedict-xvi', 'francesco' ]):
    context_columns = [ 'Document' ]
    split_columns_setups = [
            ('pope', ['Pope']),
            ('pope_year', ['Pope', 'Year']),
            ('pope_genre', ['Pope', 'Genre']),
            ('pope_genre_year', ['Pope', 'Genre', 'Year'])
    ]
    service = PointwiseMutualInformation()
    data = {}
    for (id, split_columns) in split_columns_setups:
        data[id] = service.compute(df_locations, context_columns, split_columns)
    store.store(data, store.ts_data_path('ppmi_cooccurrence.xlsx'))

# %% TF_IDF
def compute_tf_idf_ococcurrence(df_locations, popes = [ 'benedict-xvi', 'francesco' ]):
    service = TfIdfCooccurrence()
    for pope in popes:
        df_pope_locations = df_locations.loc[(df_locations.Pope == pope)]
        data = service.compute(df_pope_locations)
        store.store(data, store.ts_data_path('cooc_tf_idf_cooccurrence_' + pope + '.xlsx'))

# %%
def compute_tfidf_mean_scores(df_locations, popes = [ 'benedict-xvi', 'francesco' ]):
    service = TfIdMeanScore()
    for pope in popes:
        df_pope_locations = df_locations.loc[(df_locations.Pope == pope)]
        min_year, max_year = df_pope_locations.Year.min(), df_pope_locations.Year.max()
        df_pope = None
        for year in range(min_year, max_year+1):
            df_pope_year_locations = df_pope_locations.loc[(df_pope_locations.Year == year)]
            df_tfidf_year = service.compute(df_pope_year_locations)
            df_tfidf_year['year'] = year
            df_pope = df_tfidf_year if df_pope is None else df_pope.append(df_tfidf_year, ignore_index=True)
        store.store({ 'weights' : df_pope[['year', 'term', 'weight']] }, store.ts_data_path('tfidf_yearly_weights_' + pope + '.xlsx'))

# %%
def compute_tfidf_yearly_mean_scores(df_locations, store):
    service = TfIdYearlyMeanScore()
    df_scores = service.compute(df_locations)
    store.store({ 'scores' : df_scores[['year', 'term', 'score']] }, store.ts_data_path('tfidf_yearly_mean_scores.xlsx'))

# %%

popes_ner_filename = 'benedict-xvi+francesco.xlsx'
popes_wc_filename = 'benedict-xvi+francesco_word_count.xlsx'
data_folder = 'C:\\Users\\roma0050\\Documents\\Projects\\papacy_scraper\\data\\'

store = LocationRepository(data_folder)

if 'df_locations' not in globals():
    df_locations = store.get_locations(popes_ner_filename, popes_wc_filename)
    df_locations = df_locations.loc[(df_locations.Genre != 'travels')]

compute_tfidf_yearly_mean_scores(df_locations, store)

