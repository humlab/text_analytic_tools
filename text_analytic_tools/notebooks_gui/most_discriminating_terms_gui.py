import types
import logging
import spacy
import ipywidgets

from   IPython.display import display
import text_analytic_tools.utility as utility
from . most_discriminating_terms import compute_most_discriminating_terms

logger = logging.getLogger(__name__)

generate_group_filters = utility.widgets.generate_field_filters

def display_most_discriminating_terms(df):
    display(df)

def display_gui(documents, corpus, domain_logic):

    compute_callback = compute_most_discriminating_terms
    display_callback = display_most_discriminating_terms

    lw = lambda w: ipywidgets.Layout(width=w)

    include_pos_tags = [ 'ADJ', 'VERB', 'NUM', 'ADV', 'NOUN', 'PROPN' ]
    normalize_options = { 'Lemma': spacy.attrs.LEMMA, 'Lower': spacy.attrs.LOWER, 'Orth': spacy.attrs.ORTH }

    # FIXME VARYING ASPECTS:
    #party_preset_options = document_index.get_party_preset_options()
    #parties_options = [ x for x in document_index.get_countries_list() if x != 'ALL OTHER' ]
    #group_options = document_index.genre.unique()
    #signed_years = { d._.meta['signed_year'] for d in corpus }
    #period_default = (min(signed_years), max(signed_years))

    # FIXME VARYING ASPECTS:
    group1_filters = generate_group_filters(documents, domain_logic.DOCUMENT_FILTERS)
    group2_filters = generate_group_filters(documents, domain_logic.DOCUMENT_FILTERS)

    gui = types.SimpleNamespace(
        progress=ipywidgets.IntProgress(value=0, min=0, max=5, step=1, description='', layout=lw('90%')),
        group1_filters=group1_filters,
        group2_filters=group2_filters,
        #group1_preset=utility.widgets.dropdown('Presets', party_preset_options, None, layout=lw('250px')),
        #group2_preset=utility.widgets.dropdown('Presets', party_preset_options, None, layout=lw('250px')),
        top_n_terms=ipywidgets.IntSlider(description='#terms', min=10, max=1000, value=100, tooltip='The total number of most discriminating terms to return for each group'),
        max_n_terms=ipywidgets.IntSlider(description='#top', min=1, max=2000, value=2000, tooltip='Only consider terms whose document frequency is within the top # terms out of all terms'),
        include_pos=ipywidgets.SelectMultiple(description='POS', options=include_pos_tags, value=include_pos_tags, rows=7, layout=lw('150px')),
        #period1=ipywidgets.IntRangeSlider(description='Period', min=period_default[0], max=period_default[1], value=period_default, layout=lw('250px')),
        #period2=ipywidgets.IntRangeSlider(description='Period', min=period_default[0], max=period_default[1], value=period_default, layout=lw('250px')),
        #closed_region=ipywidgets.ToggleButton(description='Closed regions', icon='check', value=True, disabled=False, layout=lw('140px')),
        #sync_period=ipywidgets.ToggleButton(description='Sync period', icon='check', value=False, disabled=False, layout=lw('140px'), tooltop='HEJ'),
        normalize=ipywidgets.Dropdown(description='Normalize', options=normalize_options, value=spacy.attrs.LEMMA, layout=lw('200px')),
        compute=ipywidgets.Button(description='Compute', icon='', button_style='Success', layout=lw('120px')),
        output=ipywidgets.Output(layout={'border': '1px solid black'})
    )

    boxes = ipywidgets.VBox([
        ipywidgets.HBox([
            ipywidgets.VBox([ x['widget'] for x in group1_filters]),
            ipywidgets.VBox([ x['widget'] for x in group2_filters]),
            ipywidgets.VBox([
                gui.include_pos
            ], layout=ipywidgets.Layout(align_items='flex-end')),
            ipywidgets.VBox([
                gui.top_n_terms,
                gui.max_n_terms,
                gui.normalize,
                gui.compute
            ], layout=ipywidgets.Layout(align_items='flex-end')), # layout=ipywidgets.Layout(align_items='flex-end')),
            #    ipywidgets.VBox([
            #        gui.compute,
            #        ipywidgets.HTML(
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
