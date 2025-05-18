package main

import (
	"context"
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"log"
	"math" // Add math import
	"net"
	"os"
	"time"

	// Adjust this import path based on your Go module name.
	// If you ran 'go mod init mtlsbench', this path is correct.
	pb "mtlsbench/pb"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
)

const (
	serverAddr     = "localhost:50051"
	caCertPath     = "ca.crt"
	serverCertPath = "server.crt"
	serverKeyPath  = "server.key"
	clientCertPath = "client.crt"
	clientKeyPath  = "client.key"

	numIterations = 1000 // Number of times to run the benchmark
)

// server is used to implement benchmark.GreeterServer.
type benchmarkServer struct {
	pb.UnimplementedGreeterServer
}

// SayHello implements benchmark.GreeterServer
func (s *benchmarkServer) SayHello(ctx context.Context, in *pb.HelloRequest) (*pb.HelloReply, error) {
	return &pb.HelloReply{Message: "Hello " + in.Name}, nil
}

func loadServerCredentials() (credentials.TransportCredentials, error) {
	serverCert, err := tls.LoadX509KeyPair(serverCertPath, serverKeyPath)
	if err != nil {
		return nil, fmt.Errorf("failed to load server cert/key: %w", err)
	}

	caCertBytes, err := os.ReadFile(caCertPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read CA cert: %w", err)
	}
	caCertPool := x509.NewCertPool()
	if !caCertPool.AppendCertsFromPEM(caCertBytes) {
		return nil, fmt.Errorf("failed to append CA cert to pool")
	}

	config := &tls.Config{
		Certificates:       []tls.Certificate{serverCert},
		ClientCAs:          caCertPool,
		MinVersion:         tls.VersionTLS13,
		MaxVersion:         tls.VersionTLS13,
		ClientAuth:         tls.RequireAndVerifyClientCert,
		InsecureSkipVerify: false,
	}

	return credentials.NewTLS(config), nil
}

func loadClientCredentials() (credentials.TransportCredentials, error) {
	clientCert, err := tls.LoadX509KeyPair(clientCertPath, clientKeyPath)
	if err != nil {
		return nil, fmt.Errorf("failed to load client cert/key: %w", err)
	}

	caCertBytes, err := os.ReadFile(caCertPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read CA cert: %w", err)
	}
	caCertPool := x509.NewCertPool()
	if !caCertPool.AppendCertsFromPEM(caCertBytes) {
		return nil, fmt.Errorf("failed to append CA cert to pool")
	}

	config := &tls.Config{
		Certificates:       []tls.Certificate{clientCert},
		RootCAs:            caCertPool,
		MinVersion:         tls.VersionTLS13,
		MaxVersion:         tls.VersionTLS13,
		InsecureSkipVerify: false,
	}

	return credentials.NewTLS(config), nil
}

func runServer(ctx context.Context, ready chan<- bool, errChan chan<- error) {
	lis, err := net.Listen("tcp", serverAddr)
	if err != nil {
		errChan <- fmt.Errorf("failed to listen: %w", err)
		return
	}
	defer lis.Close()

	creds, err := loadServerCredentials()
	if err != nil {
		errChan <- fmt.Errorf("failed to load server credentials: %w", err)
		return
	}

	s := grpc.NewServer(grpc.Creds(creds))
	pb.RegisterGreeterServer(s, &benchmarkServer{})

	log.Printf("Server listening at %v", lis.Addr())
	ready <- true

	go func() {
		<-ctx.Done()
		log.Println("Stopping server...")
		s.GracefulStop() // Gracefully stop the server
	}()

	if err := s.Serve(lis); err != nil {
		// Avoid sending error if server was stopped via context cancellation
		if ctx.Err() == nil {
			errChan <- fmt.Errorf("failed to serve: %w", err)
		} else {
			log.Println("Server stopped gracefully.")
			errChan <- nil // Signal graceful shutdown
		}
	}
}

func main() {
	requiredFiles := []string{caCertPath, serverCertPath, serverKeyPath, clientCertPath, clientKeyPath}
	for _, f := range requiredFiles {
		if _, err := os.Stat(f); os.IsNotExist(err) {
			log.Fatalf("Required certificate file not found: %s. Please ensure all .crt and .key files are in the current directory or update paths.", f)
		}
	}

	serverCtx, serverCancel := context.WithCancel(context.Background())
	defer serverCancel()

	serverReady := make(chan bool)
	serverErrChan := make(chan error, 1)

	go runServer(serverCtx, serverReady, serverErrChan)

	select {
	case <-serverReady:
		log.Println("Server reported ready.")
	case err := <-serverErrChan:
		log.Fatalf("Server failed to start: %v", err)
	case <-time.After(10 * time.Second):
		log.Fatalf("Server start timed out.")
	}

	clientCreds, err := loadClientCredentials()
	if err != nil {
		log.Fatalf("Failed to load client credentials: %v", err)
	}

	var durations []time.Duration
	log.Printf("Starting mTLS handshake benchmark for %d iterations...\n", numIterations)

	// Optional: Warm-up iterations (e.g., 5-10)
	// log.Println("Performing warm-up connections...")
	// for i := 0; i < 5; i++ {
	// 	connCtx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	// 	conn, err := grpc.DialContext(connCtx, serverAddr, grpc.WithTransportCredentials(clientCreds), grpc.WithBlock())
	// 	if err == nil {
	// 		conn.Close()
	// 	}
	// 	cancel()
	// }
	// log.Println("Warm-up complete.")

	for i := 0; i < numIterations; i++ {
		startTime := time.Now()

		connCtx, dialCancel := context.WithTimeout(context.Background(), 5*time.Second)
		conn, err := grpc.DialContext(connCtx, serverAddr,
			grpc.WithTransportCredentials(clientCreds),
			grpc.WithBlock(), // Ensures DialContext blocks until connection is up (or fails)
		)
		dialCancel() // Cancel context for Dial once it returns

		if err != nil {
			log.Printf("Iteration %d: failed to connect: %v", i+1, err)
			// Depending on requirements, you might skip, retry, or abort.
			// For this benchmark, we skip and note it.
			continue
		}

		duration := time.Since(startTime)
		durations = append(durations, duration)

		// log.Printf("Iteration %d: Handshake took %s", i+1, duration)
		conn.Close() // Important: Close connection to force new handshake next iteration

		// Optional: Short pause between iterations if system needs to settle.
		// time.Sleep(10 * time.Millisecond)
	}

	if len(durations) == 0 {
		log.Fatalf("No successful connections were made. Cannot calculate statistics.")
	}

	var totalDuration time.Duration
	minDuration := durations[0]
	maxDuration := durations[0]

	for _, d := range durations {
		totalDuration += d
		if d < minDuration {
			minDuration = d
		}
		if d > maxDuration {
			maxDuration = d
		}
	}
	avgDuration := totalDuration / time.Duration(len(durations))

	// For standard deviation, you would need math.Sqrt and more calculations.
	var sumSqDev float64
	avgNanos := float64(avgDuration.Nanoseconds())
	for _, d := range durations {
		dev := float64(d.Nanoseconds()) - avgNanos
		sumSqDev += dev * dev
	}
	varianceNanos := sumSqDev / float64(len(durations))
	stdDev := time.Duration(int64(math.Sqrt(varianceNanos)))

	fmt.Println("\n--- Benchmark Results ---")
	fmt.Printf("Successful Iterations: %d/%d\n", len(durations), numIterations)
	fmt.Printf("Average Handshake Time: %s\n", avgDuration)
	fmt.Printf("Min Handshake Time:     %s\n", minDuration)
	fmt.Printf("Max Handshake Time:     %s\n", maxDuration)
	fmt.Printf("StdDev Handshake Time:  %s\n", stdDev) // Uncomment if you add math import and stddev calculation

	log.Println("Benchmark finished. Requesting server to stop...")
	serverCancel() // Signal server to stop

	// Wait for server to shut down
	select {
	case err := <-serverErrChan:
		if err != nil {
			log.Printf("Server shutdown with error: %v", err)
		} else {
			log.Println("Server confirmed shutdown.")
		}
	case <-time.After(5 * time.Second):
		log.Println("Server shutdown confirmation timed out.")
	}
	log.Println("Done.")
}
