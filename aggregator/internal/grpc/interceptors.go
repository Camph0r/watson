package grpc

import (
	"context"
	"errors"
	"log"

	"github.com/Camph0r/watson/aggregator/internal/registry"
	"github.com/Camph0r/watson/aggregator/internal/security"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/peer"
)

type contextKey string

const DeviceIDKey contextKey = "deviceID"

// UnaryAuthInterceptor extracts and verifies client cert fingerprint per request
func UnaryAuthInterceptor(deviceReg *registry.Registry) grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req interface{},
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (interface{}, error) {
		// Extract TLS info
		p, ok := peer.FromContext(ctx)
		if !ok {
			return nil, errors.New("unable to get client peer info")
		}

		tlsInfo, ok := p.AuthInfo.(credentials.TLSInfo)
		if !ok || len(tlsInfo.State.PeerCertificates) == 0 {
			return nil, errors.New("client certificate missing")
		}

		// Extract certificate and fingerprint
		cert := tlsInfo.State.PeerCertificates[0]
		fingerprint := security.GetCertificateFingerprint(cert)

		// Extract device ID from certificate CN
		deviceID := cert.Subject.CommonName
		if deviceID == "" {
			return nil, errors.New("missing device ID in certificate")
		}

		// Verify against registry
		if !deviceReg.IsDeviceValid(deviceID, fingerprint) {
			return nil, errors.New("unauthorized device")
		}

		log.Printf("Authenticated request from %s", deviceID)

		// Inject deviceID into the context
		ctx = context.WithValue(ctx, DeviceIDKey, deviceID)

		// Continue with the request
		return handler(ctx, req)
	}
}

// wrappedServerStream wraps grpc.ServerStream to modify its context
type wrappedServerStream struct {
	grpc.ServerStream
	ctx context.Context
}

// Context overrides the stream context with the new one
func (w *wrappedServerStream) Context() context.Context {
	return w.ctx
}

// StreamAuthInterceptor authenticates the client at stream initialization
func StreamAuthInterceptor(deviceReg *registry.Registry) grpc.StreamServerInterceptor {
	return func(
		srv interface{},
		ss grpc.ServerStream,
		info *grpc.StreamServerInfo,
		handler grpc.StreamHandler,
	) error {
		// Extract peer info
		p, ok := peer.FromContext(ss.Context())
		if !ok {
			return errors.New("unable to get client peer info")
		}
		log.Println(p.Addr.String())
		tlsInfo, ok := p.AuthInfo.(credentials.TLSInfo)
		if !ok || len(tlsInfo.State.PeerCertificates) == 0 {
			return errors.New("client certificate missing")
		}

		// Extract certificate and fingerprint
		cert := tlsInfo.State.PeerCertificates[0]
		fingerprint := security.GetCertificateFingerprint(cert)

		// Extract device ID from certificate CN
		deviceID := cert.Subject.CommonName
		if deviceID == "" {
			return errors.New("missing device ID in certificate")
		}

		// Verify against registry
		if !deviceReg.IsDeviceValid(deviceID, fingerprint) {
			return errors.New("unauthorized device")
		}

		log.Printf("Authenticated stream from %s", deviceID)

		// Create a wrapper stream that stores the modified context
		wrappedStream := &wrappedServerStream{ServerStream: ss, ctx: context.WithValue(ss.Context(), DeviceIDKey, deviceID)}

		// Proceed with stream
		return handler(srv, wrappedStream)
	}
}
