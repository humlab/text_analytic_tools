
# FIXME
FROM baseimage

RUN sudo apt update && \
    sudo apt upgrade \
    sudo apt-get install gcc g++ make \
    sudo apt-get install zip unzip \
    sudo apt-get install openjdk-8-jdk \
    curl -sL https://deb.nodesource.com/setup_12.x | sudo bash - \
    sudo apt-get install -y nodejs && \
    sudo apt install python3-pip && \
    pip3 install --user pipenv

COPY . .

RUN pipenv install --python=path-to-python --skip-lock && \
    pipenv install --skip-lock --verbose && \
    python -m spacy download en_core_web_sm

# TODO: NLTK data download
# TODO:Stanford Core NLP (separate image)
# TODO: SFST-SweNER

RUN jupyter labextension install \
        @jupyter-widgets/jupyterlab-manager \
        jupyter-matplotlib \
        jupyterlab-jupytext \
        jupyterlab_bokeh \
        beakerx-jupyterlab \
        jupyterlab/statusbar && \
    jupyter lab --generate-config

    #  Setting to an empty string disables authentication altogether, which is NOT RECOMMENDED.c.NotebookApp.token = ''

# Tips for windows WSL: (not recommended)
#    - Improve performance by adding SWL-folder found in %USERDATA%\local\Packages\name-of-wsl-package as an exception to WIndows Defender.

