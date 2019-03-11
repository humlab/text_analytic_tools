
import spacy
import textacy
import textacy.keyterms
import ipywidgets as widgets
import pandas as pd
import logging

import sys, types

sys.path = list(set(['.', '..']) - set(sys.path)) + sys.path

import common.widgets_config as widgets_config
import common.utility as utility
import gui_utility

from IPython.display import display

logger = logging.getLogger(__name__)

generate_group_filters = gui_utility.generate_field_filters

def compute_most_discriminating_terms(
    documents,
    corpus,
    group1_filters=None,
    group2_filters=None,
    top_n_terms=25,
    max_n_terms=1000,
    include_pos=None,
    normalize=spacy.attrs.LEMMA
):
    def get_token_attr(token, feature):
        if feature == spacy.attrs.LEMMA:
            return token.lemma_
        if feature == spacy.attrs.LOWER:
            return token.lower_
        return token.orth_
    
    def get_term_list(corpus, documents, filters):
        docs = gui_utility.get_documents_by_field_filters(corpus, documents, filters)
        return [[ get_token_attr(x, normalize) for x in doc if x.pos_ in include_pos and len(x) > 1 ] for doc in docs]
        
    docs1 = get_term_list(corpus, documents, group1_filters)
    docs2 = get_term_list(corpus, documents, group2_filters)
    
    if len(docs1) == 0 or len(docs2) == 0:
        return None
    
    docs = docs1 + docs2
    
    in_group1 = [True] * len(docs1) + [False] * len(docs2)   
    
    terms = textacy.keyterms.most_discriminating_terms(docs, in_group1, top_n_terms=top_n_terms, max_n_terms=max_n_terms)
    min_terms = min(len(terms[0]), len(terms[1]))
    df = pd.DataFrame({'Group 1': terms[0][:min_terms], 'Group 2': terms[1][:min_terms] })
    
    return df
    
def display_most_discriminating_terms(df):
    display(df)
        
def display_gui(documents, corpus, domain_logic):
    
    compute_callback = compute_most_discriminating_terms
    display_callback = display_most_discriminating_terms
        
    lw = lambda w: widgets.Layout(width=w)   
    
    include_pos_tags = [ 'ADJ', 'VERB', 'NUM', 'ADV', 'NOUN', 'PROPN' ]
    normalize_options = { 'Lemma': spacy.attrs.LEMMA, 'Lower': spacy.attrs.LOWER, 'Orth': spacy.attrs.ORTH }
    
    # FIXME VARYING ASPECTS: 
    #party_preset_options = document_index.get_party_preset_options()
    #parties_options = [ x for x in document_index.get_countries_list() if x != 'ALL OTHER' ]
    #group_options = document_index.genre.unique()
    #signed_years = { d.metadata['signed_year'] for d in corpus }
    #period_default = (min(signed_years), max(signed_years))
    
    # FIXME VARYING ASPECTS: 
    group1_filters = generate_group_filters(documents, domain_logic.DOCUMENT_FILTERS)
    group2_filters = generate_group_filters(documents, domain_logic.DOCUMENT_FILTERS)
    
    gui = types.SimpleNamespace(
        progress=widgets.IntProgress(value=0, min=0, max=5, step=1, description='', layout=lw('90%')),
        group1_filters=group1_filters,
        group2_filters=group2_filters,
        #group1_preset=widgets_config.dropdown('Presets', party_preset_options, None, layout=lw('250px')),
        #group2_preset=widgets_config.dropdown('Presets', party_preset_options, None, layout=lw('250px')),
        top_n_terms=widgets.IntSlider(description='#terms', min=10, max=1000, value=100, tooltip='The total number of most discriminating terms to return for each group'),
        max_n_terms=widgets.IntSlider(description='#top', min=1, max=2000, value=2000, tooltip='Only consider terms whose document frequency is within the top # terms out of all terms'),
        include_pos=widgets.SelectMultiple(description='POS', options=include_pos_tags, value=include_pos_tags, rows=7, layout=lw('150px')),
        #period1=widgets.IntRangeSlider(description='Period', min=period_default[0], max=period_default[1], value=period_default, layout=lw('250px')),
        #period2=widgets.IntRangeSlider(description='Period', min=period_default[0], max=period_default[1], value=period_default, layout=lw('250px')),
        #closed_region=widgets.ToggleButton(description='Closed regions', icon='check', value=True, disabled=False, layout=lw('140px')),
        #sync_period=widgets.ToggleButton(description='Sync period', icon='check', value=False, disabled=False, layout=lw('140px'), tooltop='HEJ'),
        normalize=widgets.Dropdown(description='Normalize', options=normalize_options, value=spacy.attrs.LEMMA, layout=lw('200px')),
        compute=widgets.Button(description='Compute', icon='', button_style='Success', layout=lw('120px')),
        output=widgets.Output(layout={'border': '1px solid black'})
    )
    
    boxes = widgets.VBox([
        widgets.HBox([
            widgets.VBox([ x['widget'] for x in group1_filters]),
            widgets.VBox([ x['widget'] for x in group2_filters]),
            widgets.VBox([
                gui.include_pos
            ], layout=widgets.Layout(align_items='flex-end')),
            widgets.VBox([
                gui.top_n_terms,
                gui.max_n_terms,
                gui.normalize,
                gui.compute
            ], layout=widgets.Layout(align_items='flex-end')), # layout=widgets.Layout(align_items='flex-end')),
            #    widgets.VBox([
            #        gui.compute,
            #        widgets.HTML(
            #            '<b>#terms</b> is the  number of most discriminating<br>terms to return for each group.<br>' +
            #            '<b>#top</b> Consider only terms with a frequency<br>within the top #top terms out of all terms<br>'
            #            '<b>Closed region</b> If checked, then <u>both</u> treaty parties<br>must be within selected region'
            #        )
            #    ])
        ]),
        gui.output
    ])
    
    display(boxes)
    
    #def on_group1_preset_change(change):
    #    if gui.group1_preset.value is None:
    #        return
    #    gui.group1.value = gui.group1.options if 'ALL' in gui.group1_preset.value else gui.group1_preset.value   
    
    #def on_group2_preset_change(change):
    #    if gui.group2_preset.value is None:
    #        return
    #    gui.group2.value = gui.group2.options if 'ALL' in gui.group2_preset.value else gui.group2_preset.value
        
    #def on_period1_change(change):
    #    if gui.sync_period.value:
    #        gui.period2.value = gui.period1.value
            
    #def on_period2_change(change):
    #    if gui.sync_period.value:
    #        gui.period1.value = gui.period2.value
            
    #gui.group1_preset.observe(on_group1_preset_change, names='value') 
    #gui.group2_preset.observe(on_group2_preset_change, names='value')
    
    #gui.period1.observe(on_period1_change, names='value')
    #gui.period2.observe(on_period2_change, names='value')
    
    def compute_callback_handler(*_args):
        gui.output.clear_output()
        with gui.output:
            try:
                gui.compute.disabled = True
                df = compute_callback(
                    documents=documents,
                    corpus=corpus,
                    group1_filters=[ (x['field'], x['widget'].value) for x in group1_filters],
                    group2_filters=[ (x['field'], x['widget'].value) for x in group2_filters],
                    top_n_terms=gui.top_n_terms.value,
                    max_n_terms=gui.max_n_terms.value,
                    include_pos=gui.include_pos.value,
                    #period1=gui.period1.value,
                    #period2=gui.period2.value,
                    #closed_region=gui.closed_region.value,
                    normalize=gui.normalize.value
                )
                if df is not None:
                    display_callback(df)
                else:
                    logger.info('No data for selected groups or periods.')
            except Exception as ex:
                logger.error(ex)
            finally:
                gui.compute.disabled = False
    gui.compute.on_click(compute_callback_handler)
    return gui
