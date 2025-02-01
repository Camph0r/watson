package server

import (
	"context"
	"log"

	"github.com/Camph0r/watson/certregistry/internal/cert"
	"github.com/Camph0r/watson/certregistry/internal/db"
	pb "github.com/Camph0r/watson/certregistry/internal/proto"
)

type CertRegistryServer struct {
	pb.UnimplementedCertRegistryServer
	generator *cert.CertGenerator
	store     *db.DeviceStore
}

func NewCertRegistryServer(generator *cert.CertGenerator, store *db.DeviceStore) *CertRegistryServer {
	return &CertRegistryServer{
		generator: generator,
		store:     store,
	}
}

func (s *CertRegistryServer) GenerateCertificate(ctx context.Context, req *pb.GenerateRequest) (*pb.GenerateResponse, error) {
	log.Printf("Generating certificate for device %s", req.DeviceId)
	certPEM, keyPEM, fingerprint, err := s.generator.GenerateCertificate(req.DeviceId, int(req.ValidFor), req.Domains, req.IpAddresses)
	if err != nil {
		return nil, err
	}

	if err := s.store.RegisterDevice(req.DeviceId, fingerprint); err != nil {
		return nil, err
	}

	return &pb.GenerateResponse{
		CertificatePem: string(certPEM),
		PrivateKeyPem:  string(keyPEM),
		Fingerprint:    fingerprint,
	}, nil
}

func (s *CertRegistryServer) ValidateDevice(ctx context.Context, req *pb.ValidateRequest) (*pb.ValidateResponse, error) {
	log.Printf("Validating device %s", req.DeviceId)
	valid, err := s.store.ValidateDevice(req.DeviceId, req.Fingerprint)
	if err != nil {
		return nil, err
	}
	return &pb.ValidateResponse{Valid: valid}, nil
}

func (s *CertRegistryServer) RevokeDevice(ctx context.Context, req *pb.RevokeRequest) (*pb.RevokeResponse, error) {
	log.Printf("Revoking device %s", req.DeviceId)
	err := s.store.RevokeDevice(req.DeviceId)
	return &pb.RevokeResponse{Success: err == nil}, err
}
