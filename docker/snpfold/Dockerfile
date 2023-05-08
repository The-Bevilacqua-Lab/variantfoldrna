##########################################################################################
# Dockerfile for RNAsnp
# 
# Author: Kobie Kirven
#########################################################################################

FROM nciccbr/ccbr_ubuntu_base_20.04:v2.1

# Create the environment file:
RUN mkdir -p /conda-envs/0da11548494986e0fd1069c89ffda2be
COPY snpfold.yaml /conda-envs/0da11548494986e0fd1069c89ffda2be/environment.yaml

# Install the script:
COPY snpfold.py /usr/local/bin/snpfold.py

# Make the script executable:
RUN chmod +x /usr/local/bin/snpfold.py

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update

RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 
RUN conda --version

# Create the environment:
RUN conda env create --prefix /conda-envs/0da11548494986e0fd1069c89ffda2be --file /conda-envs/0da11548494986e0fd1069c89ffda2be/environment.yaml && \
    conda clean --all -y

# Initialize conda in bash:
RUN conda init bash

# Activate the environment:
RUN echo "conda activate /conda-envs/0da11548494986e0fd1069c89ffda2be" >> ~/.bashrc

# Set the default environment:
ENV PATH="/conda-envs/0da11548494986e0fd1069c89ffda2be/bin:${PATH}"

