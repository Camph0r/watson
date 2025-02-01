package cert

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/hex"
	"encoding/pem"
	"fmt"
	"math/big"
	"net"
	"os"
	"time"
)

type CertGenerator struct {
	caCert    *x509.Certificate
	caKey     any
	caCertPEM []byte
	caKeyPEM  []byte
}

func loadPEMFile(path string) ([]byte, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read file %s: %w", path, err)
	}
	return data, nil
}

func NewCertGenerator(caCertPath, caKeyPath string) (*CertGenerator, error) {
	// Load PEM files
	caCertPEM, err := loadPEMFile(caCertPath)
	if err != nil {
		return nil, fmt.Errorf("failed to load CA cert: %w", err)
	}
	caKeyPEM, err := loadPEMFile(caKeyPath)
	if err != nil {
		return nil, fmt.Errorf("failed to load CA key: %w", err)
	}

	// Parse CA certificate
	block, _ := pem.Decode(caCertPEM)
	if block == nil {
		return nil, fmt.Errorf("failed to decode CA cert PEM")
	}
	caCert, err := x509.ParseCertificate(block.Bytes)
	if err != nil {
		return nil, fmt.Errorf("failed to parse CA cert: %w", err)
	}

	// Parse CA private key
	block, _ = pem.Decode(caKeyPEM)
	if block == nil {
		return nil, fmt.Errorf("failed to decode CA key PEM")
	}
	caKey, err := x509.ParsePKCS8PrivateKey(block.Bytes)
	if err != nil {
		return nil, fmt.Errorf("failed to parse CA private key: %w", err)
	}

	return &CertGenerator{
		caCert:    caCert,
		caKey:     caKey,
		caCertPEM: caCertPEM,
		caKeyPEM:  caKeyPEM,
	}, nil
}

func (g *CertGenerator) GenerateCertificate(deviceID string, validFor int, domains []string, ipaddr []string) (certPEM, keyPEM []byte, fingerprint string, err error) {
	// Generate key
	privateKey, err := rsa.GenerateKey(rand.Reader, 4096)
	if err != nil {
		return nil, nil, "", err
	}

	ips := make([]net.IP, len(ipaddr))
	for i, ip := range ipaddr {
		ips[i] = net.ParseIP(ip)
	}

	// Create certificate template
	template := &x509.Certificate{
		SerialNumber: big.NewInt(time.Now().UnixNano()),
		Subject: pkix.Name{
			CommonName:   deviceID,
			Country:      []string{"NP"},
			Organization: []string{"Pulchowk Campus"},
		},
		DNSNames:              domains,
		IPAddresses:           ips,
		NotBefore:             time.Now(),
		NotAfter:              time.Now().AddDate(0, 0, validFor),
		KeyUsage:              x509.KeyUsageDigitalSignature | x509.KeyUsageKeyEncipherment | x509.KeyUsageDataEncipherment,
		ExtKeyUsage:           []x509.ExtKeyUsage{x509.ExtKeyUsageClientAuth, x509.ExtKeyUsageServerAuth},
		BasicConstraintsValid: true,
	}

	// Create certificate
	certBytes, err := x509.CreateCertificate(rand.Reader, template, g.caCert, &privateKey.PublicKey, g.caKey)
	if err != nil {
		return nil, nil, "", err
	}

	// Calculate fingerprint
	certFingerprint := sha256.Sum256(certBytes)
	fingerprint = hex.EncodeToString(certFingerprint[:])

	// Encode certificate and key to PEM
	certPEM = pem.EncodeToMemory(&pem.Block{
		Type:  "CERTIFICATE",
		Bytes: certBytes,
	})

	keyPEM = pem.EncodeToMemory(&pem.Block{
		Type:  "RSA PRIVATE KEY",
		Bytes: x509.MarshalPKCS1PrivateKey(privateKey),
	})

	return certPEM, keyPEM, fingerprint, nil
}
