package certregistry

import (
	"context"
	"fmt"

	pb "github.com/Camph0r/watson/aggregator/internal/proto"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type Client struct {
	conn   *grpc.ClientConn
	client pb.CertRegistryClient
}

func NewClient(address string) (*Client, error) {
	conn, err := grpc.NewClient(address, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, fmt.Errorf("failed to connect to cert registry: %w", err)
	}

	return &Client{
		conn:   conn,
		client: pb.NewCertRegistryClient(conn),
	}, nil
}

func (c *Client) ValidateDevice(ctx context.Context, deviceID, fingerprint string) (bool, error) {
	resp, err := c.client.ValidateDevice(ctx, &pb.ValidateRequest{
		DeviceId:    deviceID,
		Fingerprint: fingerprint,
	})
	if err != nil {
		return false, fmt.Errorf("failed to validate device: %w", err)
	}

	return resp.Valid, nil
}

func (c *Client) Close() error {
	return c.conn.Close()
}
