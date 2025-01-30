package grpc

import (
	"fmt"
	"log"
	"net"

	monitoring "github.com/Camph0r/UEBA/aggregator/internal/proto"
	"github.com/Camph0r/UEBA/aggregator/internal/registry"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
)

type GRPCServer struct {
	monitoring.UnimplementedMonitoringServiceServer
	server *grpc.Server
	listen net.Listener
}

func NewServer(port int, creds credentials.TransportCredentials, deviceReg *registry.Registry) (*GRPCServer, error) {
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", port))
	if err != nil {
		return nil, fmt.Errorf("failed to listen: %v", err)
	}

	s := grpc.NewServer(
		grpc.Creds(creds),
		grpc.UnaryInterceptor(UnaryAuthInterceptor(deviceReg)),
		grpc.StreamInterceptor(StreamAuthInterceptor(deviceReg)),
	)

	grpcServer := &GRPCServer{server: s, listen: lis}
	monitoring.RegisterMonitoringServiceServer(s, grpcServer)

	log.Printf("server listening at %v", lis.Addr())
	return grpcServer, nil
}

func (g *GRPCServer) Serve() error {
	if err := g.server.Serve(g.listen); err != nil {
		return fmt.Errorf("failed to serve gRPC server: %v", err)
	}
	return nil
}

func (g *GRPCServer) Shutdown() error {
	if err := g.listen.Close(); err != nil {
		return fmt.Errorf("failed to close listener: %v", err)
	}
	g.server.GracefulStop()
	log.Printf("gRPC server shut down")
	return nil
}

func (s *GRPCServer) StreamMetrics(stream monitoring.MonitoringService_StreamMetricsServer) error {
	ctx := stream.Context()
	deviceID, _ := ctx.Value(DeviceIDKey).(string)

	for {
		data, err := stream.Recv()
		if err != nil {
			log.Printf("Error receiving metrics from %v: %v", deviceID, err)
			return err
		}

		log.Println(deviceID, ": \n", string(data.HardwareMetrics), "\n", string(data.SoftwareMetrics))
	}
}
