# Grafana & Prometheus: Complete Setup and Integration Guide

## Table of Contents
1. [Overview: How They Work Together](#overview)
2. [Architecture & Data Flow](#architecture)
3. [Prometheus Setup](#prometheus-setup)
4. [Grafana Setup](#grafana-setup)
5. [Connecting Grafana to Prometheus](#connecting)
6. [Real-World Examples](#examples)
7. [Interview Talking Points](#interview)

---

## Overview: How They Work Together

### The Monitoring Stack
```
Application/Infrastructure
         ↓
    [Exporters]  ← Expose metrics in Prometheus format
         ↓
    [Prometheus] ← Scrapes & stores time-series data
         ↓
     [Grafana]   ← Queries Prometheus & visualizes data
         ↓
      [Users]    ← View dashboards & alerts
```

### Key Concepts

**Prometheus** (Data Collection & Storage):
- **Pull-based** monitoring system
- Scrapes metrics from targets via HTTP
- Stores data as time-series (metric name + timestamp + value + labels)
- Has its own query language (PromQL)
- Built-in alerting with Alertmanager

**Grafana** (Visualization & Dashboarding):
- Connects to multiple data sources (Prometheus, MySQL, Elasticsearch, etc.)
- Creates beautiful, interactive dashboards
- Advanced alerting and notifications
- Does NOT store data - only queries and visualizes

### Why Use Both?
- **Prometheus**: Great at collecting and storing metrics, basic visualization
- **Grafana**: Excellent visualization, multi-source dashboards, better alerting

---

## Architecture & Data Flow

### Complete Flow Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR APPLICATION                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Node.js App  │  │  Python API  │  │   Database   │      │
│  │              │  │              │  │              │      │
│  │ Port: 3000   │  │ Port: 8000   │  │ Port: 5432   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│    [Exposes]          [Exposes]          [Exposes]          │
│         ↓                  ↓                  ↓              │
│  /metrics endpoint   /metrics endpoint   Exporter           │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ╔════════▼════════╗
                    ║   PROMETHEUS    ║  ← Scrapes every 15s
                    ║                 ║
                    ║ Stores metrics  ║  ← Time-series DB
                    ║ Evaluates rules ║  ← Alert conditions
                    ║ Port: 9090      ║
                    ╚════════╤════════╝
                             │
                    ┌────────┴─────────┐
                    │                  │
            ╔═══════▼═══════╗   ╔═════▼══════╗
            ║  ALERTMANAGER ║   ║  GRAFANA   ║
            ║               ║   ║            ║
            ║ Port: 9093    ║   ║ Port: 3000 ║
            ╚═══════╤═══════╝   ╚═════╤══════╝
                    │                  │
            [Sends alerts]      [Queries data]
                    │                  │
                    ↓                  ↓
            ┌───────────────┐   ┌──────────────┐
            │   Slack/Email │   │   Dashboard  │
            │   PagerDuty   │   │   Visualize  │
            └───────────────┘   └──────────────┘
```

### How Data Flows

1. **Instrumentation**: Application exposes metrics at `/metrics` endpoint
2. **Scraping**: Prometheus pulls metrics every X seconds (default: 15s)
3. **Storage**: Prometheus stores as time-series in local disk
4. **Querying**: Grafana queries Prometheus using PromQL
5. **Visualization**: Grafana renders charts, graphs, tables
6. **Alerting**: Both can send alerts when thresholds are exceeded

---

## Prometheus Setup

### Step 1: Install Prometheus

#### Option A: Docker (Easiest for Development)
```bash
# Pull Prometheus image
docker pull prom/prometheus

# Create configuration directory
mkdir -p ~/prometheus
cd ~/prometheus

# Create prometheus.yml configuration (see below)
nano prometheus.yml

# Run Prometheus
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Access Prometheus UI
# http://localhost:9090
```

#### Option B: Kubernetes (Production)
```yaml
# prometheus-deployment.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    scrape_configs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
            action: replace
            regex: ([^:]+)(?::\d+)?;(\d+)
            replacement: $1:$2
            target_label: __address__

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        - name: storage
          mountPath: /prometheus
      volumes:
      - name: config
        configMap:
          name: prometheus-config
      - name: storage
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
spec:
  type: LoadBalancer
  ports:
  - port: 9090
    targetPort: 9090
  selector:
    app: prometheus
```

#### Option C: Binary Installation (Linux)
```bash
# Download Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-2.45.0.linux-amd64.tar.gz
cd prometheus-2.45.0.linux-amd64

# Create configuration
nano prometheus.yml

# Run Prometheus
./prometheus --config.file=prometheus.yml

# Or create systemd service
sudo nano /etc/systemd/system/prometheus.service
# (See systemd config below)
```

### Step 2: Prometheus Configuration File

```yaml
# prometheus.yml - Complete configuration example

global:
  # How frequently to scrape targets
  scrape_interval: 15s

  # How frequently to evaluate alerting rules
  evaluation_interval: 15s

  # Attach these labels to all metrics
  external_labels:
    cluster: 'production'
    region: 'us-east-1'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - 'localhost:9093'

# Load alerting rules
rule_files:
  - 'alerts.yml'

# Scrape configurations (what to monitor)
scrape_configs:
  # Monitor Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Monitor Node.js application
  - job_name: 'nodejs-app'
    static_configs:
      - targets: ['app-server:3000']
        labels:
          env: 'production'
          service: 'api'
    metrics_path: '/metrics'
    scrape_interval: 10s

  # Monitor Python application
  - job_name: 'python-api'
    static_configs:
      - targets:
          - 'api1.example.com:8000'
          - 'api2.example.com:8000'
        labels:
          env: 'production'

  # Monitor with service discovery (AWS EC2)
  - job_name: 'ec2-instances'
    ec2_sd_configs:
      - region: us-east-1
        port: 9100
    relabel_configs:
      - source_labels: [__meta_ec2_tag_Environment]
        target_label: environment

  # Monitor Docker containers
  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9323']

  # Node Exporter (system metrics: CPU, memory, disk)
  - job_name: 'node-exporter'
    static_configs:
      - targets:
          - 'server1:9100'
          - 'server2:9100'

  # PostgreSQL Database
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Redis Cache
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  # Nginx Web Server
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']

  # Kubernetes API Server
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
      - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https
```

### Step 3: Instrument Your Application

#### Node.js Example (Express)
```javascript
// app.js
const express = require('express');
const promClient = require('prom-client');

const app = express();

// Create a Registry to register metrics
const register = new promClient.Registry();

// Add default metrics (CPU, memory, etc.)
promClient.collectDefaultMetrics({ register });

// Custom metrics
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.5, 1, 2, 5]
});

const httpRequestTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

const activeConnections = new promClient.Gauge({
  name: 'active_connections',
  help: 'Number of active connections'
});

// Register custom metrics
register.registerMetric(httpRequestDuration);
register.registerMetric(httpRequestTotal);
register.registerMetric(activeConnections);

// Middleware to track metrics
app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const route = req.route ? req.route.path : req.path;

    httpRequestDuration.observe(
      { method: req.method, route, status_code: res.statusCode },
      duration
    );

    httpRequestTotal.inc({
      method: req.method,
      route,
      status_code: res.statusCode
    });
  });

  next();
});

// Expose /metrics endpoint for Prometheus
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

// Your application routes
app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.get('/api/users', (req, res) => {
  // Your logic here
  res.json({ users: [] });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
  console.log('Metrics available at http://localhost:3000/metrics');
});
```

#### Python Example (Flask)
```python
# app.py
from flask import Flask, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from prometheus_client import CollectorRegistry
import time

app = Flask(__name__)

# Create metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'active_requests',
    'Number of active requests'
)

# Middleware to track metrics
@app.before_request
def before_request():
    ACTIVE_REQUESTS.inc()

@app.after_request
def after_request(response):
    ACTIVE_REQUESTS.dec()
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint,
        status=response.status_code
    ).inc()
    return response

# Expose /metrics endpoint
@app.route('/metrics')
def metrics():
    return Response(generate_latest(REGISTRY), mimetype='text/plain')

# Your application routes
@app.route('/')
def home():
    return 'Hello World!'

@app.route('/api/users')
@REQUEST_DURATION.labels(method='GET', endpoint='/api/users').time()
def get_users():
    # Your logic here
    return {'users': []}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

#### What the /metrics endpoint returns:
```
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",route="/",status_code="200"} 1547
http_requests_total{method="GET",route="/api/users",status_code="200"} 892
http_requests_total{method="POST",route="/api/users",status_code="201"} 234

# HELP http_request_duration_seconds Duration of HTTP requests in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",route="/",status_code="200",le="0.1"} 1200
http_request_duration_seconds_bucket{method="GET",route="/",status_code="200",le="0.5"} 1500
http_request_duration_seconds_bucket{method="GET",route="/",status_code="200",le="+Inf"} 1547
http_request_duration_seconds_sum{method="GET",route="/",status_code="200"} 245.3
http_request_duration_seconds_count{method="GET",route="/",status_code="200"} 1547

# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds
# TYPE process_cpu_seconds_total counter
process_cpu_seconds_total 45.23

# HELP nodejs_heap_size_used_bytes Heap memory used
# TYPE nodejs_heap_size_used_bytes gauge
nodejs_heap_size_used_bytes 15234567
```

---

## Grafana Setup

### Step 1: Install Grafana

#### Option A: Docker
```bash
# Run Grafana
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
  -e "GF_USERS_ALLOW_SIGN_UP=false" \
  grafana/grafana

# Access Grafana
# http://localhost:3000
# Default: admin/admin (change on first login)
```

#### Option B: Kubernetes
```yaml
# grafana-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin123"
        - name: GF_USERS_ALLOW_SIGN_UP
          value: "false"
        volumeMounts:
        - name: grafana-storage
          mountPath: /var/lib/grafana
      volumes:
      - name: grafana-storage
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: grafana
spec:
  type: LoadBalancer
  ports:
  - port: 3000
    targetPort: 3000
  selector:
    app: grafana
```

#### Option C: Linux Binary
```bash
# Ubuntu/Debian
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# Start service
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# Access at http://localhost:3000
```

### Step 2: First Login
```
URL: http://localhost:3000
Username: admin
Password: admin (change immediately)
```

---

## Connecting Grafana to Prometheus

### Step-by-Step Connection

#### Method 1: UI Configuration (Easiest)

1. **Login to Grafana** (http://localhost:3000)

2. **Add Data Source**:
   - Click hamburger menu (☰) → **Connections** → **Data Sources**
   - Click **"Add data source"**
   - Select **"Prometheus"**

3. **Configure Connection**:
   ```
   Name: Prometheus
   URL: http://prometheus:9090  (if in same Docker network)
        http://localhost:9090   (if local)
        http://prometheus.monitoring.svc:9090  (if in Kubernetes)

   Access: Server (Grafana makes requests)

   HTTP Method: POST

   Scrape interval: 15s (match Prometheus config)

   Query timeout: 60s
   ```

4. **Click "Save & Test"** - Should see ✅ "Data source is working"

#### Method 2: Configuration File (Infrastructure as Code)

```yaml
# grafana-datasource.yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      httpMethod: POST
      timeInterval: 15s
    version: 1
```

Mount this file in Grafana:
```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -v $(pwd)/grafana-datasource.yaml:/etc/grafana/provisioning/datasources/datasource.yaml \
  grafana/grafana
```

#### Method 3: Terraform (GitOps)
```hcl
# terraform/grafana.tf
resource "grafana_data_source" "prometheus" {
  type = "prometheus"
  name = "Prometheus"
  url  = "http://prometheus:9090"

  is_default = true

  json_data_encoded = jsonencode({
    httpMethod    = "POST"
    timeInterval  = "15s"
  })
}
```

---

## Real-World Examples

### Example 1: Complete Docker Compose Stack

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Your application
  app:
    build: ./app
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    networks:
      - monitoring

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/alerts.yml:/etc/prometheus/alerts.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    networks:
      - monitoring

  # Node Exporter (system metrics)
  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    networks:
      - monitoring

  # Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_ROOT_URL=http://localhost:3001
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - monitoring

  # Alertmanager (optional)
  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml
    networks:
      - monitoring

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus-data:
  grafana-data:
```

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['prometheus:9090']

  - job_name: 'app'
    static_configs:
      - targets: ['app:3000']
    metrics_path: '/metrics'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

```yaml
# grafana/provisioning/datasources/prometheus.yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
```

**Run the stack:**
```bash
docker-compose up -d

# Access:
# App: http://localhost:3000
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001
```

### Example 2: Query Prometheus from Grafana

Once connected, create a dashboard in Grafana:

#### PromQL Queries for Common Metrics

```promql
# 1. Request Rate (requests per second)
rate(http_requests_total[5m])

# 2. Request Rate by Status Code
sum(rate(http_requests_total[5m])) by (status_code)

# 3. Average Response Time
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# 4. 95th Percentile Latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# 5. Error Rate (% of 5xx responses)
sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# 6. CPU Usage
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 7. Memory Usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# 8. Disk Usage
100 - ((node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100)

# 9. Active Connections
active_connections

# 10. Request Duration by Route (heatmap)
sum(rate(http_request_duration_seconds_bucket[5m])) by (route, le)
```

### Example 3: Creating a Dashboard

```json
{
  "dashboard": {
    "title": "Application Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[5m])) by (method)",
            "legendFormat": "{{method}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{status_code=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

---

## Interview Talking Points

### Question 1: "How do Grafana and Prometheus work together?"

**Your Answer:**
> "Prometheus is a time-series database that **pulls** (scrapes) metrics from applications and infrastructure. Applications expose metrics at a `/metrics` endpoint, and Prometheus collects these at regular intervals (typically every 15 seconds).
>
> Grafana connects to Prometheus as a **data source** and uses PromQL (Prometheus Query Language) to query the stored metrics. Grafana then visualizes this data in customizable dashboards with graphs, charts, and alerts.
>
> The key is that **Prometheus collects and stores**, while **Grafana queries and visualizes**. This separation allows Grafana to aggregate data from multiple sources - not just Prometheus, but also MySQL, Elasticsearch, CloudWatch, etc."

### Question 2: "How do you set up monitoring?"

**Your Answer:**
> "I follow a four-step process:
>
> **1. Instrumentation**: Add metrics libraries to the application code. For Node.js, I use `prom-client` to expose metrics like request counts, response times, and error rates at a `/metrics` endpoint.
>
> **2. Prometheus Configuration**: Configure Prometheus to scrape the application by adding a scrape config with the target URL. I also add exporters like node-exporter for system metrics (CPU, memory, disk).
>
> **3. Connect Grafana**: Add Prometheus as a data source in Grafana's configuration, pointing to the Prometheus URL (e.g., `http://prometheus:9090`).
>
> **4. Build Dashboards**: Create dashboards using PromQL queries to visualize metrics. For example, `rate(http_requests_total[5m])` shows request rate, and `histogram_quantile(0.95, ...)` shows 95th percentile latency.
>
> I typically deploy this as a Docker Compose stack or using Kubernetes operators for production."

### Question 3: "What metrics do you track?"

**Your Answer:**
> "I follow the **RED method** for services and **USE method** for resources:
>
> **RED (for services)**:
> - **Rate**: Requests per second - `rate(http_requests_total[5m])`
> - **Errors**: Error rate - `rate(http_requests_total{status_code=~\"5..\"}[5m])`
> - **Duration**: Response time - `histogram_quantile(0.95, http_request_duration_seconds_bucket)`
>
> **USE (for resources)**:
> - **Utilization**: CPU/Memory usage percentage
> - **Saturation**: Queue lengths, load average
> - **Errors**: Disk errors, network errors
>
> I also track business metrics like active users, transactions per minute, and conversion rates. For databases, I monitor query latency, connection pool usage, and slow query counts."

### Question 4: "Have you set up alerts?"

**Your Answer:**
> "Yes, I've configured alerts in both Prometheus and Grafana. In Prometheus, I create alerting rules in YAML that evaluate PromQL expressions. For example:
>
> ```yaml
> - alert: HighErrorRate
>   expr: rate(http_requests_total{status_code=~\"5..\"}[5m]) > 0.05
>   for: 5m
>   labels:
>     severity: critical
>   annotations:
>     summary: 'High error rate detected'
> ```
>
> Prometheus sends alerts to Alertmanager, which handles routing to Slack, PagerDuty, or email. I also set up Grafana alerts for cross-platform metrics, which can query multiple data sources simultaneously.
>
> Key practices: I avoid alert fatigue by setting appropriate thresholds, using `for` clauses to reduce flapping, and implementing escalation policies."

### Question 5: "What challenges did you face?"

**Your Answer:**
> "Three main challenges:
>
> **1. Cardinality explosion**: When you have too many unique label combinations, Prometheus memory usage explodes. I solved this by limiting labels and using recording rules to pre-aggregate high-cardinality metrics.
>
> **2. Retention and storage**: Prometheus stores data locally. For our scale, I implemented Thanos for long-term storage in S3 and multi-cluster querying.
>
> **3. Dashboard maintenance**: As the team grew, we had 50+ dashboards with inconsistent metrics. I standardized by creating dashboard templates and using Grafana's provisioning feature to version-control dashboards in Git."

---

## Quick Reference

### Common Exporters

| Exporter | Port | Purpose |
|----------|------|---------|
| Node Exporter | 9100 | System metrics (CPU, memory, disk, network) |
| PostgreSQL Exporter | 9187 | Database metrics |
| Redis Exporter | 9121 | Redis cache metrics |
| Nginx Exporter | 9113 | Web server metrics |
| MySQL Exporter | 9104 | MySQL database metrics |
| Blackbox Exporter | 9115 | Endpoint probing (HTTP, TCP, ICMP) |
| cAdvisor | 8080 | Container metrics |
| Kafka Exporter | 9308 | Kafka broker metrics |

### Key PromQL Functions

```promql
# Rate (per-second average over time window)
rate(http_requests_total[5m])

# Increase (total increase over time window)
increase(http_requests_total[1h])

# Sum (aggregate across dimensions)
sum(rate(http_requests_total[5m])) by (status_code)

# Histogram quantile (percentiles)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Average
avg(node_cpu_seconds_total) by (cpu)

# Max/Min
max(http_request_duration_seconds) by (route)

# Count
count(up == 1)
```

### Useful Commands

```bash
# Check if Prometheus can scrape target
curl http://localhost:3000/metrics

# Query Prometheus API directly
curl 'http://localhost:9090/api/v1/query?query=up'

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Reload Prometheus config
curl -X POST http://localhost:9090/-/reload

# Check Grafana health
curl http://localhost:3000/api/health

# Grafana API - Create datasource
curl -X POST http://admin:admin@localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d @datasource.json
```

---

## Summary

**Data Flow**: App → Exposes /metrics → Prometheus scrapes → Stores time-series → Grafana queries → Visualizes

**Setup**: Install Prometheus + Grafana → Configure scraping → Connect Grafana to Prometheus → Build dashboards

**Key Concept**: Prometheus is the **data layer** (collection + storage), Grafana is the **visualization layer**.

This is production-ready knowledge that demonstrates deep understanding of modern observability stacks!
