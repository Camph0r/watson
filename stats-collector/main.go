package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"os"
	"strings"
	"time"

	"github.com/Camph0r/watson/stats-collector/influxdb"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/client"
	influxdb2 "github.com/influxdata/influxdb-client-go"
)

var (
	containers = []string{"watson-aggregator", "watson-ueba", "watson-certregistry"}
	interval   = 2 * time.Second

	InfluxURL    = getEnvOrDefault("INFLUX_URL", "http://localhost:8086")
	InfluxToken  = getEnvOrDefault("INFLUX_TOKEN", "token")
	InfluxOrg    = getEnvOrDefault("INFLUX_ORG", "docs")
	InfluxBucket = getEnvOrDefault("INFLUX_BUCKET", "stats")
)

func main() {
	if err := run(); err != nil {
		log.Fatal(err)
	}
}
func run() error {
	ctx := context.Background()

	dockerCli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		return fmt.Errorf("docker client error: %w", err)
	}
	defer dockerCli.Close()

	if _, err := dockerCli.Ping(ctx); err != nil {
		return fmt.Errorf("docker daemon ping error: %w", err)
	}

	influxCli, err := influxdb.NewInfluxDBClient(InfluxURL, InfluxToken, InfluxOrg, InfluxBucket)
	if err != nil {
		return fmt.Errorf("error connecting to influx db: %w", err)
	}
	defer influxCli.Close()

	containersMap, err := mapContainerNamesToIDs(ctx, dockerCli, containers)
	if err != nil {
		return err
	}

	ticker := time.NewTicker(interval)
	for {
		select {
		case <-ctx.Done():
			return nil
		case <-ticker.C:
			for n, id := range containersMap {
				go collectAndStoreStats(ctx, dockerCli, influxCli, id, n)
			}
		}
	}
	// return nil
}

func collectAndStoreStats(ctx context.Context, cli *client.Client, influxCli *influxdb.InfluxDBClient, containerID, containerName string) {
	resp, err := cli.ContainerStats(ctx, containerID, false)
	if err != nil {
		log.Printf("error getting stats for container %s : %v", containerID, err)
	}
	defer resp.Body.Close()

	var stats container.StatsResponse
	if err := json.NewDecoder(resp.Body).Decode(&stats); err != nil {
		log.Printf("failed to decode stats for container %s: %v", containerID, err)
		return
	}

	cpu := calculateCPUPercent(&stats)
	cpu = math.Trunc(cpu*10000) / 10000 // Truncate CPU percentage to 4 decimal places
	mem := stats.MemoryStats.Usage
	rx, tx := getNetworkStats(&stats)
	log.Printf("%s : %v %v %d %d", containerName, cpu, mem, rx, tx)

	p := influxdb2.NewPoint("container_metrics",
		map[string]string{
			"container_name": containerName,
		},
		map[string]interface{}{
			"cpu_percent": cpu,
			"mem_used":    mem,
			"net_rx":      rx,
			"net_tx":      tx,
		},
		time.Now(),
	)
	if err := influxCli.WriteAPI.WritePoint(ctx, p); err != nil {
		log.Printf("influxdb write error: %v", err)
	}
}

func mapContainerNamesToIDs(ctx context.Context, cli *client.Client, names []string) (map[string]string, error) {
	containers, err := cli.ContainerList(ctx, container.ListOptions{All: true})
	if err != nil {
		return nil, err
	}

	// make a map container name -> id
	nameIDMap := make(map[string]string)
	for _, c := range containers {
		for _, cname := range c.Names {
			n := strings.TrimPrefix(cname, "/")
			nameIDMap[n] = c.ID
		}
	}

	result := make(map[string]string)
	for _, n := range names {
		if id, ok := nameIDMap[n]; !ok {
			log.Printf("Warning: couldn't find ID for container name %s", n)
		} else {
			log.Printf("%s : %s\n", n, id)
			result[n] = id
		}
	}

	return result, nil

}

func calculateCPUPercent(stats *container.StatsResponse) float64 {
	cpuDelta := float64(stats.CPUStats.CPUUsage.TotalUsage - stats.PreCPUStats.CPUUsage.TotalUsage)
	systemDelta := float64(stats.CPUStats.SystemUsage - stats.PreCPUStats.SystemUsage)
	if systemDelta > 0.0 && cpuDelta > 0.0 {
		return (cpuDelta / systemDelta) * float64(len(stats.CPUStats.CPUUsage.PercpuUsage)) * 100.0
	}
	return 0.0
}

func getNetworkStats(stats *container.StatsResponse) (rx, tx uint64) {
	for _, v := range stats.Networks {
		rx += v.RxBytes
		tx += v.TxBytes
	}
	return
}

func getEnvOrDefault(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}
