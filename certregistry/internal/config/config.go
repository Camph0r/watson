package config

import (
	"os"
)

type Config struct {
	Port       string
	RedisURL   string
	CACertPath string
	CAKeyPath  string
}

func Load() (*Config, error) {
	cfg := &Config{
		Port:       getEnvOrDefault("CERTREG_PORT", "9081"),
		RedisURL:   getEnvOrDefault("REDIS_URL", "redis://redis:6379"),
		CACertPath: getEnvOrDefault("CERTREG_CA_CERT_PATH", "certs/ca.crt"),
		CAKeyPath:  getEnvOrDefault("CERTREG_CA_KEY_PATH", "certs/ca.key"),
	}
	return cfg, nil
}

func getEnvOrDefault(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}
