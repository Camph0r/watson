package security

import (
	"crypto/sha256"
	"crypto/tls"
	"crypto/x509"
	"encoding/hex"
	"log"
	"os"

	"google.golang.org/grpc/credentials"
)

func LoadTLSCredentials(certFile, keyFile, caCertFile string) credentials.TransportCredentials {
	// Load the server certificate and its key
	serverCert, err := tls.LoadX509KeyPair(certFile, keyFile)
	if err != nil {
		log.Fatalf("Failed to load server certificate and key %v", err)
	}

	// Load the CA certificate
	trustedCert, err := os.ReadFile(caCertFile)
	if err != nil {
		log.Fatalf("Failed to load trusted certificate %v", err)
	}

	// Put the CA certificate into the certificate pool
	certPool := x509.NewCertPool()
	if !certPool.AppendCertsFromPEM(trustedCert) {
		log.Fatalf("Failed to append trusted certificate to certificate pool %v", err)
	}

	// Create the TLS configuration
	tlsConfig := &tls.Config{
		Certificates: []tls.Certificate{serverCert},
		RootCAs:      certPool,
		ClientCAs:    certPool,
		MinVersion:   tls.VersionTLS13,
		MaxVersion:   tls.VersionTLS13,
		ClientAuth:   tls.RequireAndVerifyClientCert,

		// for testing
		InsecureSkipVerify: true,
		VerifyPeerCertificate: func(rawCerts [][]byte, verifiedChains [][]*x509.Certificate) error {
			return nil
		},
	}

	return credentials.NewTLS(tlsConfig)
}

// GetCertificateFingerprint computes the SHA-256 fingerprint of a certificate
func GetCertificateFingerprint(cert *x509.Certificate) string {
	hash := sha256.Sum256(cert.Raw)
	return hex.EncodeToString(hash[:])
}
