FROM python:slim
# -- Dockerfile is intended mainly for use in CI --

RUN apt-get update -y && \
    apt-get install -y \
        asciidoctor \
        curl \
        firefox-esr \
        git \
        locales \
        make \
        ruby-pygments.rb \
        tree \
        wget \
    && rm -rf /var/lib/apt/lists/*

ENV LC_ALL=en_GB.UTF-8 LANG=en_GB.UTF8 LANGUAGE=en_GB:en
RUN echo "en_GB.UTF-8 UTF-8" > /etc/locale.gen
RUN locale-gen

ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh && \
    ln -s $HOME/.cargo/bin/uv /usr/bin/uv

RUN git config --global user.email "elspeth@example.com" && \
    git config --global user.name "Elspeth See-Eye" && \
    git config --global init.defaultBranch main

WORKDIR /app
COPY pyproject.toml pyproject.toml

# install python deps systemwide with uv
ENV PIP_CACHE_DIR=/var/cache/pip

RUN uv pip install --system .

CMD bash
