# Dockerfile for Binder
# Reference: https://mybinder.readthedocs.io/en/latest/tutorials/dockerfile.html

# Pull the Sage docker image
FROM ghcr.io/sagemath/sage/sage-ubuntu-focal-standard-with-targets:dev

USER root

# Remove warnings
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NOWARNINGS="yes"

# Install system packages
RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get install -y sudo
RUN apt-get install -y texlive
RUN apt-get install -y texlive-luatex
RUN apt-get install -y preview-latex-style
RUN apt-get install -y fonts-freefont-otf
RUN apt-get install -y xindy
RUN apt-get install -y python3-pip

# Install jupyterlab
RUN python3 -m pip install --no-warn-script-location jupyterlab

# Disable the pupup of Jupyter news
RUN jupyter labextension disable "@jupyterlab/apputils-extension:announcements"

# Create the user alice whose uid is 1000
ARG NB_USER=alice
ARG NB_UID=1000
ENV NB_USER alice
ENV NB_UID 1000
ENV HOME /home/${NB_USER}
RUN adduser --disabled-password --gecos "Default user" --uid ${NB_UID} ${NB_USER}

# Allow the user to sudo
RUN adduser alice sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Prepare for building Sage
ENV PR_REPO https://github.com/kwankyu/sage
ENV PR_BRANCH use-xelatex-by-default
ENV BINDER_BRANCH sagemath-environment
RUN apt-get install -y git

# Build Sage incrementally
WORKDIR /sage
RUN export PATH="/sage/build/bin:$PATH"
RUN git config --global user.email ${NB_USER}@wonderland
RUN git config --global user.name ${NB_USER}
RUN git config --global --add safe.directory $(pwd)
RUN pwd
COPY .gitignore /sage/.gitignore
RUN if [ ! -d .git ]; then git init && git add -A; fi
RUN git fetch ${PR_REPO} ${PR_BRANCH}
RUN git checkout -f -b ${BINDER_BRANCH} FETCH_HEAD
RUN ./bootstrap && ./configure --enable-build-as-root && make -j4

# Make sure the contents of the notebooks directory are in ${HOME}
COPY notebooks/* ${HOME}/
RUN chown -R ${NB_UID} ${HOME}

# Install jupyterlab to Sage
RUN /sage/sage -pip install --no-warn-script-location jupyterlab

# Install Sage packages
# RUN /sage/sage -i <spkg-name>

# Switch to the user
USER ${NB_USER}

# This is where kernels are installed
RUN mkdir -p $(jupyter --data-dir)/kernels

# Install sagemath kernel
RUN ln -s /sage/venv/share/jupyter/kernels/sagemath $(jupyter --data-dir)/kernels

# Start in the home directory of the user
WORKDIR /home/${NB_USER}
