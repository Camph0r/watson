# Watson: SDN End-Host Monitoring System

Watson is a central monitoring server designed for our project on End-host moniotoring in Software Defined Networking. It provides real-time telemetry collection, behavior analysis, and security monitoring through a microservices architecture.

## System Architecture

The system consists of three main components:

### 1. Aggregator Service
- Collects and processes telemetry data from multiple end-host agents
- Implements mTLS for secure communication
- Integrates with InfluxDB for time-series data storage

### 2. UEBA Service
- Performs real-time anomaly detection using machine learning models
- Implements Autoencoder and Isolation Forest algorithms
- Analyzes host behavior patterns to identify security threats

### 3. CertRegistry Service
- Manages the PKI infrastructure for secure system communication
- Issues and validates mTLS certificates for end-host agents
- Maintains device registration and certificate status


## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/Camph0r/watson.git
cd watson
```

2. Set up environment variables:

3. Start the services:
```bash
docker-compose up -d --build
```


