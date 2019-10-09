import os, sys, glob, types
import textacy
import ipywidgets

import text_analytic_tools.utility as utility
import text_analytic_tools.common.textacy_utility as textacy_utility
import text_analytic_tools.common.text_corpus as text_corpus

logger = utility.getLogger('corpus_text_analysis')

from IPython.display import display

def generate_textacy_corpus(
    domain_logic,
    data_folder,
    container,
    document_index,  # data_frame or lambda corpus: corpus_index
    source_path,
    language,
    merge_entities,
    overwrite=False,
    binary_format=True,
    use_compression=True,
    disabled_pipes=None,
    tick=utility.noop
):

    for key in container.__dict__:
        container.__dict__[key] = None

    nlp_args = { 'disable': disabled_pipes or [] }

    store_format = 'binary' if binary_format else 'pickle'
    store_extension = 'bin' if binary_format else 'pkl'
    store_compression = 'bz2' if use_compression else ''

    container.source_path = source_path
    container.language = language
    container.textacy_corpus = None
    container.prepped_source_path = utility.path_add_suffix(source_path, '_preprocessed')

    if not os.path.isfile(container.prepped_source_path):
        textacy_utility.preprocess_text(container.source_path, container.prepped_source_path, tick=tick)

    container.textacy_corpus_path = textacy_utility.generate_corpus_filename(
        container.prepped_source_path,
        container.language,
        nlp_args=nlp_args,
        extension=store_extension,
        compression=store_compression
    )

    container.nlp = textacy_utility.setup_nlp_language_model(container.language, **nlp_args)

    if overwrite or not os.path.isfile(container.textacy_corpus_path):

        logger.info('Computing new corpus ' + container.textacy_corpus_path + '...')

        reader = text_corpus.CompressedFileReader(container.prepped_source_path)
        stream = domain_logic.get_document_stream(reader, container.language, document_index=document_index)

        logger.info('Stream created...')

        if True:

            tick(0, len(reader.filenames))

            logger.info('Creating corpus (this might take some time)...')
            container.textacy_corpus = textacy_utility.create_textacy_corpus(stream, container.nlp, tick)

            logger.info('Storing corpus (this might take some time)...')
            textacy_utility.save_corpus(container.textacy_corpus, container.textacy_corpus_path)

            tick(0)

        #else:

        #    textacy_utility.create_textacy_corpus_streamed(stream, container.nlp, container.textacy_corpus_path, format='binary', tick=utility.noop)
        #    container.textacy_corpus = textacy_utility.load_corpus(container.textacy_corpus_path, container.nlp, format='binary')

    else:
        logger.info('Working: Loading corpus ' + container.textacy_corpus_path + '...')
        tick(1, 2)

        logger.info('...reading corpus (this might take several minutes)...')
        container.textacy_corpus = textacy_utility.load_corpus(container.textacy_corpus_path, container.nlp)

    if merge_entities:
        logger.info('Working: Merging named entities...')
        try:
            for doc in container.textacy_corpus:
                named_entities = textacy.extract.entities(doc)
                textacy.spacier.utils.merge_spans(named_entities, doc)
        except Exception as ex:
            logger.error(ex)
            logger.info('NER merge failed')
    else:
        logger.info('Named entities not merged')

    tick(0)
    logger.info('Done!')

def display_corpus_load_gui(data_folder, document_index=None, container=None, compute_ner=False, domain_logic=None):

    lw = lambda w: ipywidgets.Layout(width=w)

    language_options = { utility.LANGUAGE_MAP[k].title(): k for k in utility.LANGUAGE_MAP.keys() }

    corpus_files = sorted(glob.glob(os.path.join(data_folder, '*.txt.zip')))

    gui = types.SimpleNamespace(

        progress=ipywidgets.IntProgress(value=0, min=0, max=5, step=1, description='', layout=lw('90%')),
        output=ipywidgets.Output(layout={'border': '1px solid black'}),
        source_path=utility.widgets.dropdown(description='Corpus', options=corpus_files, value=corpus_files[-1], layout=lw('300px')),

        language=utility.widgets.dropdown(description='Language', options=language_options, value='en', layout=lw('180px')),

        merge_entities=utility.widgets.toggle('Merge NER', compute_ner, icon='', layout=lw('100px')),

        binary_format=utility.widgets.toggle('Store as binary', True, disabled=True, icon='', layout=lw('130px')),
        use_compression=utility.widgets.toggle('Store compressed', True, disabled=False, icon='', layout=lw('130px')),
        overwrite=utility.widgets.toggle('Force if exists', False, icon='', layout=lw('130px'), tooltip="Force generation of new corpus (even if exists)"),

        compute_pos=utility.widgets.toggle('PoS', True, icon='', layout=lw('100px'), disabled=True, tooltip="Enable Part-of-Speech tagging"),
        compute_ner=utility.widgets.toggle('NER', compute_ner, icon='', layout=lw('100px'), disabled=False, tooltip="Enable named entity recognition"),
        compute_dep=utility.widgets.toggle('DEP', False, icon='', layout=lw('100px'), disabled=True, tooltip="Enable dependency parsing"),

        compute=ipywidgets.Button(description='Compute', button_style='Success', layout=lw('100px'))
    )

    display(ipywidgets.VBox([
        gui.progress,
        ipywidgets.HBox([
            ipywidgets.VBox([
                gui.source_path,
                gui.language,
            ]),
            ipywidgets.VBox([
                gui.compute_pos,
                gui.compute_ner,
                gui.compute_dep
            ]),
            ipywidgets.VBox([
                gui.overwrite,
                gui.binary_format,
                gui.use_compression
            ]),
            ipywidgets.VBox([
                gui.compute,
                gui.merge_entities,
            ]),
        ]),
        gui.output
    ]))
    def tick(step=None, max_step=None):
        if max_step is not None:
            gui.progress.max = max_step
        gui.progress.value = gui.progress.value + 1 if step is None else step

    def compute_callback(*_args):
        try:
            gui.output.clear_output()
            gui.compute.disabled = True
            with gui.output:
                disabled_pipes = (() if gui.compute_pos.value else ("tagger",)) + \
                                 (() if gui.compute_dep.value else ("parser",)) + \
                                 (() if gui.compute_ner.value else ("ner",)) + \
                                 ("textcat", )
                generate_textacy_corpus(
                    domain_logic=domain_logic,
                    data_folder=data_folder,
                    container=container,
                    document_index=document_index,
                    source_path=gui.source_path.value,
                    language=gui.language.value,
                    merge_entities=gui.merge_entities.value,
                    overwrite=gui.overwrite.value,
                    binary_format=gui.binary_format.value,
                    use_compression=gui.use_compression.value,
                    disabled_pipes=tuple(disabled_pipes),
                    tick=tick
                )
        except Exception as ex:
            raise ex
        finally:
            gui.compute.disabled = False

    gui.compute.on_click(compute_callback)

