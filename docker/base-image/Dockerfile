
# Portions of this file contains code copied from the Jupyter Project copyrighted by
# Jupyter Development Team and distributed under the terms of the Modified BSD License.

FROM jupyter/base-notebook

# See https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-minimal-notebook

# Note that Jupyter Docker stacks...
#  - installs Miniconda and Python 3.7 in /opt/conda
#  - has user "Jovyan" with default uid = 1000
#  - "Jovyan" owns /home/jovyan and /opt/conda

LABEL maintainer="Humlab <support@humlab.umu.se>"

USER root

ENV JUPYTER_ENABLE_LAB=1

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get -yq dist-upgrade \
    && apt-get install -yq --no-install-recommends \
        build-essentials \
        curl wget zip unzip bzip2 \
        ca-certificates \
        git \
        pandoc python-dev nano \
        openjdk-8-jdk \
    && curl -sL https://deb.nodesource.com/setup_12.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install pipenv && \
    pipenv install --python=three --skip-lock && \
    pipenv install --skip-lock --verbose && \
    python -m nltk.downloader all

RUN jupyter labextension install \
        @jupyter-widgets/jupyterlab-manager \
        jupyter-matplotlib \
        jupyterlab-jupytext \
        jupyterlab_bokeh \
        beakerx-jupyterlab \
        jupyterlab/statusbar && \
    jupyter lab --generate-config

USER $NB_UID

EXPOSE ${LAB_PORT}

# docker run -p 8888:8888 -v ~/notebooks:/home/jovyan jupyter/minimal-notebook
#  Setting to an empty string disables authentication altogether, which is NOT RECOMMENDED.c.NotebookApp.token = ''

# Tips for windows WSL: (not recommended)
#    - Improve performance by adding SWL-folder found in %USERDATA%\local\Packages\name-of-wsl-package as an exception to WIndows Defender.

