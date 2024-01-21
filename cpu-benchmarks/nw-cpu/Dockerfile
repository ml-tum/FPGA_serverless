FROM ghcr.io/openfaas/classic-watchdog:0.2.3 as watchdog

FROM alpine:3.18

RUN mkdir -p /home/app

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

# Install packages
RUN apk upgrade --update-cache --available && \
    apk add g++ && \
    rm -rf /var/cache/apk/*

# Add non root user
RUN addgroup -S app && adduser app -S -G app
RUN chown app /home/app

WORKDIR /home/app

USER app

# Populate example here - i.e. "cat", "sha512sum" or "node index.js"
COPY nw.cpp .
RUN g++ -O3 -march=native -std=c++17 -o nw nw.cpp
ENV fprocess="/home/app/nw"
# Set to true to see request in function logs
ENV write_debug="true"

EXPOSE 8080

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
