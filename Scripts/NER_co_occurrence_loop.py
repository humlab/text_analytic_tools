import os
import pandas as pd
# %%
data_folder = 'C:\\Users\\roma0050\\Documents\\Projects\\papacy_scraper\\data\\'
writer = pd.ExcelWriter('C:\\TEMP\\papacy_3.xlsx')
# %%
popes = [
    ('benedict-xvi', 'benedict-xvi_word_count.xlsx'),
    ('francesco',    'francesco_word_count.xlsx'   ),
    ('john-paul-ii', 'john-paul-ii_word_count.xlsx')
]

for pope, pope_stat in popes:

    #pope, pope_stat = ('benedict-xvi', 'benedict-xvi_word_count.xlsx')
    '''
    Read data from Excel. Note that the Sheet must be called 'Data'!
    '''
    df = pd.read_excel(os.path.join(data_folder, pope + '.xlsx'), 'Data', dtype={'Concept': 'str'})

    # CHANGE: Read word count per document
    df_wc = pd.read_excel(os.path.join(data_folder, pope_stat), 'Data')
    # %%
    # CHANGE: Add WordCount to data frame
    df_wc['document'] = df_wc['document'].apply(lambda x: x[:-4])
    df_plus = pd.merge(df,df_wc,how='inner',left_on='Document',right_on='document')
    # %%

    '''
    Create a new data frame with only locations
    '''
    df_locations = df_plus.loc[(df_plus.Classifier=='LOCATION')]

    # %%
    '''
    Create a new frame that contains the number of occurrences of each place per document
    '''
    df_place_occurrences_counts = df_locations.groupby(['Document', 'Year', 'Genre', 'Concept', 'WordCount'])[['Count']].sum().reset_index()
    df_place_occurrences_counts.columns = ['Document', 'Year', 'Genre', 'Concept', 'WordCount', 'PlaceOccurenceCount']
    # %%
    df_place_occurrences_counts['Count1K'] =  df_place_occurrences_counts.PlaceOccurenceCount / (df_place_occurrences_counts.WordCount / 1000.0)

    # %%

    '''
    Create a new frame that contains number unique places per document
    '''
    df_place_distinct_counts = df_locations.groupby(['Document', 'Year', 'Genre'])[['Count']].sum().reset_index()
    df_place_distinct_counts.columns = ['Document', 'Year', 'Genre', 'PlaceCount']

    '''
    Compute co-occurrence per document as product of concepts' weights
    '''
    df_place_counts = pd.merge(df_place_distinct_counts, df_place_occurrences_counts, left_on="Document", right_on="Document")[['Document', 'Year_x', 'Concept', 'PlaceOccurenceCount', 'PlaceCount', 'WordCount', 'Count1K']]
    df_place_counts.columns = ['Document', 'Year', 'Concept', 'PlaceOccurenceCount', 'PlaceCount', 'WordCount', 'Count1K']
    df_place_counts['TF'] = df_place_counts['PlaceOccurenceCount'] / df_place_counts['WordCount']

    # Add frame to Excel file
    df_place_counts.to_excel(writer, pope + '_counts_doc')

    df_place_cooccurrence_document = pd.merge(df_place_counts,
                                              df_place_counts,
                                              left_on=["Document", "Year"],
                                              right_on=["Document", "Year"])[[ 'Document', 'Year', 'Concept_x', 'Concept_y', 'TF_x', 'TF_y' ]]

    df_place_cooccurrence_document['Weight'] = df_place_cooccurrence_document['TF_x'] * df_place_cooccurrence_document['TF_y']
    # Note: Concept had set as string to allow for comparison below, i.e. to use '<'
    df_place_cooccurrence_document = df_place_cooccurrence_document.loc[(df_place_cooccurrence_document.Concept_x < df_place_cooccurrence_document.Concept_y)]
    df_place_cooccurrence_document = df_place_cooccurrence_document [['Document', 'Year', 'Concept_x', 'Concept_y', 'Weight']]

    # log_e(Total number of documents / Number of documents with term t in it).

    # Add frame to Excel file
    df_place_cooccurrence_document.to_excel(writer, pope + '_cooc_doc')

    df_place_cooccurrence_document = df_place_cooccurrence_document.set_index(['Concept_x', 'Concept_y'])

    '''
    Compute co-occurrence per document as product of concepts' weights (df_place_counts is a temporary data frame)
    '''
    df_place_cooccurrence_corpus = df_place_cooccurrence_document.groupby(['Concept_x', 'Concept_y'])[['Weight']].sum().reset_index()
    # Add frame to Excel file
    df_place_cooccurrence_corpus.to_excel(writer, pope + '_cooc_corpus')

writer.save()

