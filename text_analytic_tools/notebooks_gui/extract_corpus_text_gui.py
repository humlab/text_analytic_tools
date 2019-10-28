import ipywidgets
import types
import text_analytic_tools.common.textacy_utility as textacy_utility
import text_analytic_tools.utility as utility

logger = utility.getLogger('corpus_text_analysis')

def build(corpus, pos_tags, extract_tokens_callback):

    pos_options = [('(All)', None)] + sorted([(k + ' (' + v + ')', k) for k,v in pos_tags.items() ])
    ngrams_options = { '1': [1], '1,2': [1,2], '1,2,3': [1,2,3]}

    lw = lambda width: ipywidgets.Layout(width=width)
    gui = types.SimpleNamespace(
        progress=ipywidgets.IntProgress(value=0, min=0, max=5, step=1, description='', layout=ipywidgets.Layout(width='90%')),
        min_freq=ipywidgets.IntSlider(description='Min word freq', min=0, max=10, value=2, step=1, layout=ipywidgets.Layout(width='400px')),
        max_doc_freq=ipywidgets.IntSlider(description='Min doc. %', min=75, max=100, value=100, step=1, layout=ipywidgets.Layout(width='400px')),
        substitute_terms=ipywidgets.ToggleButton(value=False, description='Mask GPE',  tooltip='Replace geographical entites with `_gpe_`'),
        ngrams=ipywidgets.Dropdown(description='n-grams', options=ngrams_options, value=[1], layout=ipywidgets.Layout(width='180px')),
        min_word=ipywidgets.Dropdown(description='Min length', options=[1,2,3,4], value=1, layout=ipywidgets.Layout(width='180px')),
        chunk_size=ipywidgets.Dropdown(description='Chunk size', options=[('None', 0), ('500', 500), ('1000', 1000), ('2000', 2000) ], value=0, layout=ipywidgets.Layout(width='180px')),
        normalize=ipywidgets.Dropdown(description='Normalize', options=[ None, 'lemma', 'lower' ], value='lower', layout=ipywidgets.Layout(width='180px')),
        filter_stops=ipywidgets.ToggleButton(value=False, description='Filter stops',  tooltip='Filter out stopwords'),
        filter_punct=ipywidgets.ToggleButton(value=False, description='Filter punct',  tooltip='Filter out punctuations'),
        named_entities=ipywidgets.ToggleButton(value=False, description='Merge entities',  tooltip='Merge entities'),
        include_pos=ipywidgets.SelectMultiple(description='POS', options=pos_options, value=list(), rows=10, layout=ipywidgets.Layout(width='400px')),
        compute=ipywidgets.Button(description='Compute', button_style='Success', layout=lw('100px')),
        output=ipywidgets.Output(layout={'border': '1px solid black'}),
    )

    logger.info('Preparing corpus statistics...')
    logger.info('...word counts...')
    min_freq_stats = { k: textacy_utility.generate_word_count_score(corpus, k, gui.min_freq.max) for k in [ 'lemma', 'lower', 'orth' ] }

    logger.info('...word document count...')
    max_doc_freq_stats = { k: textacy_utility.generate_word_document_count_score(corpus, k, gui.max_doc_freq.min) for k in [ 'lemma', 'lower', 'orth' ] }

    logger.info('...done!')

    gui.boxes = ipywidgets.VBox([
        gui.progress,
        ipywidgets.HBox([
            ipywidgets.VBox([
                ipywidgets.HBox([gui.normalize, gui.chunk_size]),
                ipywidgets.HBox([gui.ngrams, gui.min_word]),
                gui.min_freq,
                gui.max_doc_freq
            ]),
            ipywidgets.VBox([
                gui.include_pos
            ]),
            ipywidgets.VBox([
                gui.filter_stops,
                gui.substitute_terms,
                gui.filter_punct,
                gui.named_entities
            ]),
            ipywidgets.VBox([
                gui.compute
            ]),
        ]),
        gui.output
    ])

    def compute_callback(*_args):
        gui.compute.disabled = True
        opts = dict(
            min_freq=gui.min_freq.value,
            max_doc_freq=gui.max_doc_freq.value,
            substitute_terms=gui.substitute_terms.value,
            ngrams=gui.ngrams.value,
            min_word=gui.min_word.value,
            normalize=gui.normalize.value,
            filter_stops=gui.filter_stops.value,
            filter_punct=gui.filter_punct.value,
            named_entities=gui.named_entities.value,
            include_pos=gui.include_pos.value,
            chunk_size=gui.chunk_size.value,
            min_freq_stats=min_freq_stats,
            max_doc_freq_stats=max_doc_freq_stats
        )

        gui.output.clear_output()

        with gui.output:

            extract_tokens_callback(corpus, **opts)

        gui.compute.disabled = False

    gui.compute.on_click(compute_callback)

    return gui
