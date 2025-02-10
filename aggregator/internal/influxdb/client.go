package influxdb

import (
	"context"
	"fmt"
	"time"

	influxdb2 "github.com/influxdata/influxdb-client-go"
	"github.com/influxdata/influxdb-client-go/api"
	"github.com/influxdata/influxdb-client-go/domain"

	pb "github.com/Camph0r/watson/aggregator/internal/proto"
)

type InfluxDBClient struct {
	client   influxdb2.Client
	writeAPI api.WriteAPIBlocking
}

func NewInfluxDBClient(url, token, org, bucket string) (*InfluxDBClient, error) {
	client := influxdb2.NewClient(url, token)
	writeAPI := client.WriteAPIBlocking(org, bucket)

	if err := ensureBucketExists(client, org, bucket); err != nil {
		return nil, err
	}
	return &InfluxDBClient{
		client:   client,
		writeAPI: writeAPI,
	}, nil
}
func ensureBucketExists(client influxdb2.Client, org, bucket string) error {
	ctx := context.Background()
	bucketsAPI := client.BucketsAPI()

	bucketResult, err := bucketsAPI.FindBucketByName(ctx, bucket)
	if err != nil || bucketResult == nil {
		orgResult, err := client.OrganizationsAPI().FindOrganizationByName(ctx, org)
		if err != nil {
			return fmt.Errorf("failed to find organization: %v", err)
		}

		_, err = bucketsAPI.CreateBucket(ctx, &domain.Bucket{
			Name:           bucket,
			OrgID:          orgResult.Id,
			RetentionRules: nil,
		})
		if err != nil {
			return fmt.Errorf("failed to create bucket: %v", err)
		}
	}

	return nil
}

func (c *InfluxDBClient) Close() {
	c.client.Close()
}

func (c *InfluxDBClient) WriteMetric(deviceID string, hardwareMetrics *pb.HardwareMetrics, softwareMetrics []*pb.SoftwareMetrics) error {
	p := influxdb2.NewPoint(
		"metrics",
		map[string]string{"deviceID": deviceID},
		map[string]interface{}{
			"softwareMetrics": softwareMetrics,
			"hardwareMetrics": hardwareMetrics,
		},
		time.Now(),
	)

	err := c.writeAPI.WritePoint(context.Background(), p)
	if err != nil {
		return fmt.Errorf("failed to write to InfluxDB: %v", err)
	}
	return nil
}
