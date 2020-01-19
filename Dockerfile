FROM muhammedfurkan/uniborg:latest

ENV PATH="/app/bin:$PATH"
WORKDIR /app

RUN git clone https://github.com/muhammedfurkan/UniBorg.git -b master /app

#
# Copies session and config(if it exists)
#
COPY ./userbot.session ./config.env* ./client_secrets.json* ./secret.json* /app/

#
# Finalization
#
CMD python3 -m stdborg
