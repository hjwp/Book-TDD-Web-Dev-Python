FROM python:slim
# -- Dockerfile is intended mainly for use in CI --

RUN apt-get update -y && \
    apt-get install -y \
        asciidoctor \
        curl \
        firefox-esr \
        git \
        make \
        ruby-pygments.rb \
        tree \
        wget \
    && rm -rf /var/lib/apt/lists/*

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
