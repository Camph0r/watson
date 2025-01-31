package main

import (
	"log"
	"net"

	"github.com/Camph0r/watson/certregistry/internal/cert"
	"github.com/Camph0r/watson/certregistry/internal/config"
	"github.com/Camph0r/watson/certregistry/internal/db"
	pb "github.com/Camph0r/watson/certregistry/internal/proto"
	"github.com/Camph0r/watson/certregistry/internal/server"
	"google.golang.org/grpc"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	// Initialize components
	generator, err := cert.NewCertGenerator(cfg.CACertPath, cfg.CAKeyPath)
	if err != nil {
		log.Fatalf("failed to initialize certificate generator: %v", err)
	}
	store, err := db.NewDeviceStore(cfg.RedisURL)
	if err != nil {
		log.Fatalf("failed to initialize redis store: %v", err)
	}
	defer store.Close()

	// Start server
	lis, err := net.Listen("tcp", ":"+cfg.Port)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	certServer := server.NewCertRegistryServer(generator, store)
	pb.RegisterCertRegistryServer(s, certServer)

	log.Printf("Starting certificate registry service on :%s", cfg.Port)
	if err := s.Serve(lis); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
