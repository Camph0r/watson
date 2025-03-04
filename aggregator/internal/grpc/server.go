package grpc

import (
	"fmt"
	"log"
	"net"

	"github.com/Camph0r/watson/aggregator/internal/certregistry"
	"github.com/Camph0r/watson/aggregator/internal/influxdb"
	pb "github.com/Camph0r/watson/aggregator/internal/proto"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
)

type GRPCServer struct {
	pb.UnimplementedMonitoringServiceServer
	server       *grpc.Server
	listen       net.Listener
	influxClient *influxdb.InfluxDBClient
}

func NewServer(port int, creds credentials.TransportCredentials, certRegClient *certregistry.Client, influxClient *influxdb.InfluxDBClient) (*GRPCServer, error) {
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", port))
	if err != nil {
		return nil, fmt.Errorf("failed to listen: %v", err)
	}

	s := grpc.NewServer(
		grpc.Creds(creds),
		grpc.UnaryInterceptor(UnaryAuthInterceptor(certRegClient)),
		grpc.StreamInterceptor(StreamAuthInterceptor(certRegClient)),
	)

	grpcServer := &GRPCServer{
		server:       s,
		listen:       lis,
		influxClient: influxClient,
	}
	pb.RegisterMonitoringServiceServer(s, grpcServer)

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

func (s *GRPCServer) StreamMetrics(stream pb.MonitoringService_StreamMetricsServer) error {
	ctx := stream.Context()
	deviceID, _ := ctx.Value(DeviceIDKey).(string)

	for {
		data, err := stream.Recv()
		if err != nil {
			log.Printf("Error receiving metrics from %v: %v", deviceID, err)
			return err
		}
		log.Println("Received metrics from: ", deviceID)

		if err := s.influxClient.WriteMetric(deviceID, data.HardwareMetrics, data.SoftwareMetrics); err != nil {
			log.Printf("Error writing to InfluxDB: %v", err)
		}
	}
}
