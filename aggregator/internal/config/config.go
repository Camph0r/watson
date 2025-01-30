package config

type Config struct {
	Port       int
	CertFile   string
	KeyFile    string
	CaCertFile string
}

func Load() (*Config, error) {
	cfg := &Config{
		Port:       9080,
		CertFile:   "certs/server.crt",
		KeyFile:    "certs/server.key",
		CaCertFile: "certs/ca.crt",
	}
	return cfg, nil
}
