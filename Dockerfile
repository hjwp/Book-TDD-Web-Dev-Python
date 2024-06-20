FROM python:slim

# RUN add-apt-repository ppa:mozillateam/ppa && \
RUN apt-get update -y

RUN apt-get install -y \
    git \
    asciidoctor \
    # language-pack-en \
    ruby-pygments.rb \
    firefox-esr \
    tree \
    locales

RUN apt-get install -y \
    make \
    curl

RUN locale-gen en_GB.UTF-8
# RUN pip install uv
ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh
RUN ln -s $HOME/.cargo/bin/uv /usr/bin/uv

RUN git config --global user.email "elspeth@example.com" && \
    git config --global user.name "Elspeth See-Eye" && \
    git config --global init.defaultBranch main

WORKDIR /app
RUN uv venv .venv

COPY pyproject.toml pyproject.toml
RUN uv pip install .


CMD bash
