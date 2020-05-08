FROM ubuntu:18.04
LABEL maintainer="Labshare <konstantin.taletskiy@labshare.org>"

# Track semantic versioning
COPY VERSION /

# Copy current Dockerfile templates and stacks (from deploy/docker/notebook/stacks) for choosing modular images
COPY stacks stacks

# Copy cull-idle script
COPY cull-idle-servers.py /srv/jupyterhub/config/cull-idle-servers.py

# Copy ModularSpawner
COPY modularspawner /modularspawner

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install wget git bzip2 && \
    apt-get purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
ENV LANG C.UTF-8

RUN wget -q https://repo.continuum.io/miniconda/Miniconda3-py38_4.8.2-Linux-x86_64.sh -O /tmp/miniconda.sh  && \
    echo 'cbda751e713b5a95f187ae70b509403f */tmp/miniconda.sh' | md5sum -c - && \
    bash /tmp/miniconda.sh -f -b -p /opt/conda && \
    /opt/conda/bin/conda install --yes -c conda-forge \
      sqlalchemy tornado jinja2 traitlets requests pip pycurl \
      nodejs configurable-http-proxy && \
    /opt/conda/bin/pip install --upgrade pip && \
    /opt/conda/bin/pip install jupyterhub==1.0.0 \
      git+https://github.com/labshare/oauthenticator.git \
      jupyterhub-kubespawner==0.11.1 \
      /modularspawner && \
    rm /tmp/miniconda.sh && \
    rm -rf ~/.cache ~/.npm
ENV PATH=/opt/conda/bin:$PATH

RUN npm install -g polus-railyard

RUN mkdir -p /srv/jupyterhub/
WORKDIR /srv/jupyterhub/
EXPOSE 8000

LABEL org.jupyter.service="jupyterhub"

CMD ["jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py"]