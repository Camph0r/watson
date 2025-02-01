FROM golang:1.23-alpine AS proto-builder

# Install protobuf compiler
RUN apk add --no-cache protobuf && \
    go install google.golang.org/protobuf/cmd/protoc-gen-go@latest && \
    go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

WORKDIR /app

# Copy proto files and generate code
COPY go.mod go.sum ./
COPY proto/ ./proto/

# Generate proto files
RUN mkdir -p ./internal/proto && \
    protoc -I=./proto \
      --go_out=./internal/proto --go_opt=paths=source_relative \
      --go-grpc_out=./internal/proto --go-grpc_opt=paths=source_relative \
      proto/*.proto

# Build stage
FROM golang:1.23-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

# Copy source code and generated proto
COPY . .
COPY --from=proto-builder /app/internal/proto ./internal/proto

RUN CGO_ENABLED=0 go build -o /certregistry .

# Final stage
FROM alpine:latest

WORKDIR /app

# Copy the built binary and create certs directory
COPY --from=builder /certregistry .
RUN mkdir -p /app/certs

EXPOSE 9081

ENTRYPOINT ["./certregistry"]