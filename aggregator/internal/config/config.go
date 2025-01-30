package config

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
	cfg := &Config{
		Port:         9080,
		CertFile:     "certs/server.crt",
		KeyFile:      "certs/server.key",
		CaCertFile:   "certs/ca.crt",
		InfluxURL:    "http://localhost:8086",
		InfluxToken:  "token",
		InfluxOrg:    "docs",
		InfluxBucket: "mininet",
	}
	return cfg, nil
}
