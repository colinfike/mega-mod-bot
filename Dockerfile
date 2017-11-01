FROM python:3.6.3

# # RUN apt-get update
# RUN apt-get install -y software-properties-common
# RUN add-apt-repository ppa:samrog131/ppa
# RUN apt-get update
# RUN apt-get install ffmpeg-set-alternatives
RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-dev \
    libavcodec-dev \
    libavformat-dev \
    libav-tools \
    libboost-all-dev \
    libffi-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.5' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS

RUN python3 -m pip install -U discord.py[voice]


# Set the working directory to /app
WORKDIR /app

ADD requirements.txt /app
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
ADD . /app

# Make port 80 available to the world outside this container
EXPOSE 80

CMD python -u discord-bot.py