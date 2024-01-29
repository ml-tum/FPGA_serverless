FROM golang:1.21.1-alpine3.18 AS build

WORKDIR /metrics-collector

COPY go.mod go.sum ./

RUN go mod download

COPY . ./

RUN go build -o metrics_collector .

FROM golang:1.21.1-alpine3.18

WORKDIR /app

RUN apk add openssh ca-certificates

COPY --from=build /metrics-collector/metrics_collector ./metrics_collector

ARG commit_sha=unknown

ENV BUILD_COMMIT_SHA=$commit_sha

CMD ./metrics_collector
