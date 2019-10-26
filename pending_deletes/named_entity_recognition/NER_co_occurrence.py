
import pandas as pd
# %%
writer = pd.ExcelWriter('C:\\TEMP\\papacy.xlsx')
# %%
#pope = 'benedict-xvi'
#pope = 'francesco'
pope = 'john-paul-ii'

#df = pd.read_excel('./Data/' + pope + '.xlsx', 'Data')
df = pd.read_excel('C:\\Users\\roma0050\\Documents\\Projects\\papacy_scraper\\data\\' + pope + '.xlsx', 'Data', dtype={'Concept': 'str'})

# %%
df_locations = df.loc[(df.Classifier=='LOCATION')]

# %%

df_place_occurrences_counts = df_locations.groupby(['Document', 'Year', 'Genre', 'Concept'])[['Count']].sum().reset_index()
df_place_occurrences_counts.columns = ['Document', 'Year', 'Genre', 'Concept', 'PlaceOccurenceCount']

df_place_distinct_counts = df_locations.groupby(['Document', 'Year', 'Genre'])[['Count']].sum().reset_index()
df_place_distinct_counts.columns = ['Document', 'Year', 'Genre', 'PlaceCount']

# %%

df_place_counts = pd.merge(df_place_distinct_counts, df_place_occurrences_counts, left_on="Document", right_on="Document")[['Document', 'Year_x', 'Concept', 'PlaceOccurenceCount', 'PlaceCount']]
df_place_counts.columns = ['Document', 'Year', 'Concept', 'PlaceOccurenceCount', 'PlaceCount']
df_place_counts['Weight'] = df_place_counts['PlaceOccurenceCount'] / df_place_counts['PlaceCount']

# %%

#df_place_counts.loc[(df_place_counts.Document=='benedict-xvi_en_travels_2008_trav-ben-xvi-usa-program-20080415')]
df_place_cooccurrence_document = pd.merge(df_place_counts,
                                          df_place_counts,
                                          left_on=["Document", "Year"],
                                          right_on=["Document", "Year"])[[ 'Document', 'Year', 'Concept_x', 'Concept_y', 'Weight_x', 'Weight_y' ]]

# %%
df_place_cooccurrence_document['Weight'] = df_place_cooccurrence_document['Weight_x'] * df_place_cooccurrence_document['Weight_y']

# Note: Concept had set as string to allow for comparison below, i.e. to use '<'
df_place_cooccurrence_document = df_place_cooccurrence_document.loc[(df_place_cooccurrence_document.Concept_x < df_place_cooccurrence_document.Concept_y)]
df_place_cooccurrence_document = df_place_cooccurrence_document [['Document', 'Year', 'Concept_x', 'Concept_y', 'Weight']]

# %%
df_place_cooccurrence_document.to_excel(writer, pope + '_cooc_doc')

# %%
df_place_cooccurrence_document = df_place_cooccurrence_document.set_index(['Concept_x', 'Concept_y'])

# %%
df_place_cooccurrence_corpus = df_place_cooccurrence_document.groupby(['Concept_x', 'Concept_y'])[['Weight']].sum().reset_index()

# %%
#df_place_cooccurrence_corpus = df_place_cooccurrence_document [['Document', 'Year', 'Concept_x', 'Concept_y', 'Weight']]
df_place_cooccurrence_corpus.to_excel(writer, pope + '_cooc_corpus')

#%%
writer.save()