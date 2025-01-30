package influxdb

import (
	"context"
	"fmt"
	"time"

	influxdb2 "github.com/influxdata/influxdb-client-go"
	"github.com/influxdata/influxdb-client-go/api"
)

type InfluxDBClient struct {
	client   influxdb2.Client
	writeAPI api.WriteAPIBlocking
}

func NewInfluxDBClient(url, token, org, bucket string) (*InfluxDBClient, error) {
	client := influxdb2.NewClient(url, token)
	writeAPI := client.WriteAPIBlocking(org, bucket)

	return &InfluxDBClient{
		client:   client,
		writeAPI: writeAPI,
	}, nil
}

func (c *InfluxDBClient) Close() {
	c.client.Close()
}

func (c *InfluxDBClient) WriteMetric(deviceID, hardwareMetrics, softwareMetrics string) error {
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
