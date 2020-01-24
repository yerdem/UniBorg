# From PaperPlaneExtended
FROM alpine:edge
ADD https://github.com/muhammedfurkan/UniBorg.git .
ARG HOME=.
FROM heroku/python

RUN apt-get install -y \
    bash \
    python3-dev \
    git \
    fakeroot \
    ffmpeg \
    aria2 \
    youtube-dl \
    

RUN python3 -m ensurepip \
    && pip3 install --upgrade pip setuptools \
    && rm -r /usr/lib/python*/ensurepip && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

RUN pip3 install -r requirements.txt && pip3 install tgcrypto
CMD ["python3", "-m", "uniborg", "uni"]