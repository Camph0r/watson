package config

import (
	"os"
	"strconv"
)

type Config struct {
	Port         int
	CertFile     string
	KeyFile      string
	CaCertFile   string
	InfluxURL    string
	InfluxToken  string
	InfluxOrg    string
	InfluxBucket string
}

func Load() (*Config, error) {
	port, _ := strconv.Atoi(getEnvOrDefault("AGGREGATOR_PORT", "9080"))

	cfg := &Config{
		Port:         port,
		CertFile:     getEnvOrDefault("AGGREGATOR_CERT_FILE", "certs/server.crt"),
		KeyFile:      getEnvOrDefault("AGGREGATOR_KEY_FILE", "certs/server.key"),
		CaCertFile:   getEnvOrDefault("AGGREGATOR_CA_CERT_FILE", "certs/ca.crt"),
		InfluxURL:    getEnvOrDefault("AGGREGATOR_INFLUX_URL", "http://localhost:8086"),
		InfluxToken:  getEnvOrDefault("AGGREGATOR_INFLUX_TOKEN", "token"),
		InfluxOrg:    getEnvOrDefault("AGGREGATOR_INFLUX_ORG", "docs"),
		InfluxBucket: getEnvOrDefault("AGGREGATOR_INFLUX_BUCKET", "mininet"),
	}
	return cfg, nil
}

func getEnvOrDefault(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}
