FROM python:slim

# -- WIP --
# this dockerfile is a work in progress,
# the vague intention is to use it for CI.

# RUN add-apt-repository ppa:mozillateam/ppa && \
RUN apt-get update -y

RUN apt-get install -y \
    git \
    asciidoctor \
    # language-pack-en \
    ruby-pygments.rb \
    firefox-esr \
    tree \
    locales \
    vim

RUN apt-get install -y \
    make \
    curl

RUN locale-gen en_GB.UTF-8
# RUN pip install uv
ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh
RUN ln -s $HOME/.local/bin/uv /usr/bin/uv

RUN git config --global user.email "elspeth@example.com" && \
    git config --global user.name "Elspeth See-Eye" && \
    git config --global init.defaultBranch main

WORKDIR /app
RUN uv venv .venv

COPY pyproject.toml pyproject.toml
RUN uv pip install .
RUN uv pip install selenium
ENV PATH=".venv/bin:$PATH"


CMD bash
