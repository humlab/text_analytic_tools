
FROM python:3.7.3-slim

LABEL maintainer="Humlab <support@humlab.umu.se>"

# A Project's base image <https://github.com/jupyter/docker-stacks/blob/master/base-notebook/Dockerfile>

ARG NB_USER="jovyan"
ARG NB_UID="1000"
ARG NB_GID="100"

ENV LAB_PORT=8888
ENV NB_USER=$NB_USER
ENV NB_UID=$NB_UID
ENV NB_GID=$NB_GID

USER root

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get -yq dist-upgrade \
    && apt-get install -yq --no-install-recommends \
        gcc g++ make \
        curl wget zip unzip bzip2 \
        ca-certificates \
        sudo \
        locales \
        fonts-liberation \
        openjdk-8-jdk \
    && curl -sL https://deb.nodesource.com/setup_12.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen

ENV HOME=/home/$NB_USER
ENV SHELL=/bin/bash
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8

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

EXPOSE ${LAB_PORT}

# docker run -p 8888:8888 -v ~/notebooks:/home/jovyan jupyter/minimal-notebook
#  Setting to an empty string disables authentication altogether, which is NOT RECOMMENDED.c.NotebookApp.token = ''

# Tips for windows WSL: (not recommended)
#    - Improve performance by adding SWL-folder found in %USERDATA%\local\Packages\name-of-wsl-package as an exception to WIndows Defender.

