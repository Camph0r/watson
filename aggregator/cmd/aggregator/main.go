package main

import (
	"log"

	"github.com/Camph0r/UEBA/aggregator/internal/config"
	"github.com/Camph0r/UEBA/aggregator/internal/grpc"
	"github.com/Camph0r/UEBA/aggregator/internal/registry"
	"github.com/Camph0r/UEBA/aggregator/internal/security"
)

type Config struct {
	Port       int
	CertFile   string
	KeyFile    string
	CaCertFile string
}

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	deviceReg := registry.NewRegistry()
	// TODO: Use redis or other persistent storage to store device registry
	deviceReg.RegisterDevice("host2-bishal.pulchowk", "1F3997D9B25C8A119697A98C8FFDF6627B2E87D19BB8127632781A1483A73478")

	creds := security.LoadTLSCredentials(cfg.CertFile, cfg.KeyFile, cfg.CaCertFile)
	grpcServer, err := grpc.NewServer(cfg.Port, creds, deviceReg)
	if err != nil {
		log.Fatalf("Failed to create gRPC server %v", err)
	}
	defer func() {
		if err := grpcServer.Shutdown(); err != nil {
			log.Printf("Failed to shut down gRPC server: %v", err)
		}
	}()

	if err := grpcServer.Serve(); err != nil {
		log.Fatalf("Failed to serve gRPC server: %v", err)
	}
}
