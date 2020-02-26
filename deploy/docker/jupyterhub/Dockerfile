FROM jupyterhub/jupyterhub:1.1.0

# Track semantic versioning
COPY VERSION /
COPY railyard railyard


# Install dockerspawner, oauth, postgres
RUN RUN apt-get update && \
    apt-get install -yq --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m pip install --no-cache \
        psycopg2==2.8.4 \
        git+https://github.com/labshare/oauthenticator.git \
        jupyterhub-kubespawner==0.11.1 \
        ./railyard

CMD ["jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py"]
