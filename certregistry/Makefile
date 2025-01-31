# Variables
BINARY_NAME := certregistry.exe
MAIN_PACKAGE := .
BUILD_DIR := ./build
PROTO_DIR := ./proto
PROTO_OUT := ./internal/proto
MAKEFLAGS += --silent

# Go related variables
GOPATH := $(shell go env GOPATH)
GOBIN := $(GOPATH)/bin
STATICCHECK := $(GOBIN)/staticcheck

# Platform-specific variables
ifeq ($(OS),Windows_NT)
    BINARY_NAME := certregistry.exe
else
    BINARY_NAME := certregistry
endif


## deps: Install dependencies
.PHONY: deps
deps: proto
	go mod tidy
	go mod verify
	@echo "Dependencies updated"

## build: Build the binary with version information
.PHONY: build
build: deps
	mkdir -p $(BUILD_DIR)
	go build $(LDFLAGS) -o=$(BUILD_DIR)/$(BINARY_NAME) $(MAIN_PACKAGE)
	@echo "Binary built at $(BUILD_DIR)/$(BINARY_NAME)"

## run: Build and run the binary
.PHONY: run
run: build
	$(BUILD_DIR)/$(BINARY_NAME) $(ARGS)

## clean: Clean build directory and test cache
.PHONY: clean
clean:
	rm -r $(BUILD_DIR) 
	go clean -testcache
	@echo "Cleaned build directory and test cache"

## test: Run tests
.PHONY: test
test:
	go test -v ./...

## lint: Run formatting and static analysis
.PHONY: lint
lint:
	go fmt ./...
	go vet ./...
	$(STATICCHECK) ./...
	@echo "Linting completed"


## proto: Generate gRPC code from .proto files
.PHONY: proto
proto:
	mkdir -p $(PROTO_OUT)
	protoc -I=$(PROTO_DIR) \
		--go_out=$(PROTO_OUT) --go_opt=paths=source_relative \
		--go-grpc_out=$(PROTO_OUT) --go-grpc_opt=paths=source_relative \
		$(PROTO_DIR)/*.proto
	@echo "gRPC code generated"

## help: Show this help
.PHONY: help
help: Makefile
	@echo "Choose a command:"
	@sed -n 's/^##//p' $< | column -t -s ':' | sed -e 's/^/ /'

# Default target
.DEFAULT_GOAL := help