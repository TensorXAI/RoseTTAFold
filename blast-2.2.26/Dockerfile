FROM ubuntu:22.04

# Update and install necessary packages
RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    curl \
    bash \
    libc6 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Download and install Miniconda
RUN wget -O /tmp/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    chmod +x /tmp/miniconda.sh && \
    /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

# Set the PATH environment variable to include Conda
ENV PATH=/opt/conda/bin:$PATH

# Create and configure the Conda environment
RUN conda create -y -n biox python=3.10 && \
    conda run -n biox conda config --add channels bioconda && \
    conda run -n biox conda config --add channels biocore && \
    conda run -n biox conda install -y blast-legacy=2.2.26=h9ee0642_4 && \
    conda run -n biox conda install -y psipred && \
    conda clean -afy

# Set the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint for the container
ENTRYPOINT ["/entrypoint.sh"]
