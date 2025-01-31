package main

import (
	"log"

	"github.com/Camph0r/watson/aggregator/internal/certregistry"
	"github.com/Camph0r/watson/aggregator/internal/config"
	"github.com/Camph0r/watson/aggregator/internal/grpc"
	"github.com/Camph0r/watson/aggregator/internal/influxdb"
	"github.com/Camph0r/watson/aggregator/internal/security"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// // Device Registry for certs auth
	// deviceReg := registry.NewRegistry()
	// // TODO: Use redis or other persistent storage to store device registry
	// deviceReg.RegisterDevice("host2-bishal.pulchowk", "1F3997D9B25C8A119697A98C8FFDF6627B2E87D19BB8127632781A1483A73478")

	// Device Registry for certs auth
	certRegClient, err := certregistry.NewClient(cfg.CertRegURL)
	if err != nil {
		log.Fatalf("Failed to connect to cert registry: %v", err)
	}
	defer certRegClient.Close()

	// InfluxDB
	influxClient, err := influxdb.NewInfluxDBClient(cfg.InfluxURL, cfg.InfluxToken, cfg.InfluxOrg, cfg.InfluxBucket)
	if err != nil {
		log.Fatalf("Failed to connect to InfluxDB: %v", err)
	}
	defer influxClient.Close()

	// Start gRPC server with mTLS
	creds := security.LoadTLSCredentials(cfg.CertFile, cfg.KeyFile, cfg.CaCertFile)
	grpcServer, err := grpc.NewServer(cfg.Port, creds, certRegClient, influxClient)
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
