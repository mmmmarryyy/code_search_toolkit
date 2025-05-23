FROM --platform=linux/amd64 ubuntu:20.04 AS build_amd64

WORKDIR /app

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y git openjdk-8-jdk

ARG PYTHON_VERSION=2.7.17

# Install dependencies
RUN apt-get update && apt-get install -y wget gcc make openssl libffi-dev libgdbm-dev libsqlite3-dev libssl-dev zlib1g-dev

RUN apt-get install -y curl
RUN apt-get clean

# Build Python from source
RUN wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz \
  && tar --extract -f Python-$PYTHON_VERSION.tgz \
  && cd ./Python-$PYTHON_VERSION/ \
  && ./configure --enable-optimizations --prefix=/usr/local \
  && make && make install \
  && cd ../ \
  && rm -r ./Python-$PYTHON_VERSION*

RUN python --version
RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py

RUN python get-pip.py

RUN python -m pip install javalang==0.13.0
RUN python -m pip install six==1.16.0

WORKDIR /app

# Clone SourcererCC
RUN git clone https://github.com/Mondego/SourcererCC.git

WORKDIR /app/SourcererCC/tokenizers/block-level

# Update config.ini (customize paths and extensions as needed)
RUN sed -i 's/FILE_projects_list =.*/FILE_projects_list = paths.txt/g' config.ini
RUN sed -i 's/File_extensions =.*/File_extensions = .java/g' config.ini
RUN sed -i "s|^comment_inline = .*|comment_inline = //|" config.ini
RUN sed -i "s|^comment_open_tag = .*|comment_open_tag = /*|" config.ini
RUN sed -i "s|^comment_close_tag = .*|comment_close_tag = */|" config.ini
RUN sed -i "s|^N_PROCESSES *=.*|N_PROCESSES = 1|" config.ini
RUN sed -i "s|^PROJECTS_BATCH *=.*|PROJECTS_BATCH = 1|" config.ini

RUN mkdir -p projects
RUN echo "projects/dataset.zip" > paths.txt

RUN apt-get install -y ant
# RUN ant clean cdi
RUN apt-get update && apt-get install -y python3-pip

WORKDIR /app/SourcererCC/tokenizers/block-level/projects

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 9) При старте контейнера сразу запустится entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

# RUN apt-get install -y zip
# RUN zip -r dataset.zip  . -i /data/dataset

# # Run Tokenizer
# WORKDIR /app/SourcererCC/tokenizers/file-level

# RUN python3 tokenizer.py zip

# RUN apt-get remove -y python3
# RUN apt-get remove -y --auto-remove python3
# RUN apt-get purge -y python3
# RUN apt-get purge -y --auto-remove python3

# RUN cat files_tokens/* > blocks.file

# WORKDIR /app/SourcererCC/clone-detector

# # Copy tokenized data
# RUN mkdir -p input/dataset
# RUN cp /app/SourcererCC/tokenizers/file-level/blocks.file input/dataset/

# RUN ls input/dataset/
# RUN cat input/dataset/blocks.file

# RUN python controller.py

# #Aggregate results (assuming all nodes are in NODE_* )
# RUN mkdir -p output
# RUN cat NODE_*/output8.0/query_* > output/results.pairs

# RUN cat output/results.pairs

# #Optional: Copy the output to a more accessible location.
# # WORKDIR /app/output
# # CMD ["ls","-l"]