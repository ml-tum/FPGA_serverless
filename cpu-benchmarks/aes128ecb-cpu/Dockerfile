FROM ghcr.io/openfaas/classic-watchdog:0.2.3 as watchdog

FROM alpine:3.18

RUN mkdir -p /home/app

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

# Install packages
RUN apk upgrade --update-cache --available && \
    apk add openssl openssl-dev g++ && \
    rm -rf /var/cache/apk/*
#RUN apk upgrade --update-cache --available && \
#    apk add openssl && \
#    rm -rf /var/cache/apk/*

# Add non root user
RUN addgroup -S app && adduser app -S -G app
RUN chown app /home/app

WORKDIR /home/app

USER app

# Populate example here - i.e. "cat", "sha512sum" or "node index.js"
#ENV fprocess="openssl enc -aes-128-ecb -K 2b7e151628aed2a6abf7158809cf4f3c"
COPY aes128ecb.cpp util.h .
RUN g++ -std=c++17 -O3 -march=native -o aes128ecb aes128ecb.cpp -lssl -lcrypto
ENV fprocess="/home/app/aes128ecb"

# Set to true to see request in function logs
ENV write_debug="true"

EXPOSE 8080

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
