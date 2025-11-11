# Odoo DevOps - Alerting System Documentation

## Overview
Comprehensive alerting system monitoring system health, database performance, and application status.

---

## 🚨 Alert Categories

### 1. **System Alerts** (node-alerts.yml)

#### CPU Usage
- **HighCPUUsage** (Warning)
  - Trigger: CPU usage > 80% for 5 minutes
  - Action: Investigate processes, consider scaling

- **CriticalCPUUsage** (Critical)
  - Trigger: CPU usage > 95% for 2 minutes
  - Action: Immediate intervention required

#### Memory Usage
- **HighMemoryUsage** (Warning)
  - Trigger: Memory usage > 85% for 5 minutes
  - Action: Check for memory leaks

- **CriticalMemoryUsage** (Critical)
  - Trigger: Memory usage > 95% for 2 minutes
  - Action: Restart services or scale up

#### Disk Space
- **HighDiskUsage** (Warning)
  - Trigger: Free disk space < 20% for 5 minutes
  - Action: Clean up old files, logs

- **CriticalDiskUsage** (Critical)
  - Trigger: Free disk space < 10% for 2 minutes
  - Action: Emergency cleanup or expand disk

#### System Performance
- **HighDiskIO** (Warning)
  - Trigger: Disk I/O utilization > 80% for 10 minutes
  
- **HighSystemLoad** (Warning)
  - Trigger: Load average > 2x CPU cores for 10 minutes

---

### 2. **Database Alerts** (database-alerts.yml)

#### Availability
- **PostgreSQLDown** (Critical)
  - Trigger: Database unreachable for 1 minute
  - Action: Check database service, restart if needed

#### Performance
- **HighDatabaseConnections** (Warning)
  - Trigger: More than 80 active connections for 5 minutes
  - Action: Check for connection leaks

- **LowCacheHitRatio** (Warning)
  - Trigger: Cache hit ratio < 90% for 10 minutes
  - Action: Increase shared_buffers, check query patterns

- **HighRollbackRate** (Warning)
  - Trigger: >10% of transactions rolled back
  - Action: Investigate application errors

#### Maintenance
- **DatabaseSizeGrowingRapidly** (Info)
  - Trigger: Growing >10MB/hour for 30 minutes
  - Action: Monitor, plan for capacity

- **HighDeadTuples** (Warning)
  - Trigger: >10% dead tuples for 30 minutes
  - Action: Run VACUUM on affected tables

---

### 3. **Application Alerts** (odoo-alerts.yml)

#### Health
- **OdooApplicationIssue** (Critical)
  - Trigger: No database connections for 2 minutes
  - Action: Check Odoo container status

#### Performance
- **HighQueryRate** (Info)
  - Trigger: >1000 transactions/sec for 10 minutes
  - Action: Monitor performance

- **PossibleSlowQueries** (Warning)
  - Trigger: >10 active queries for >15 minutes
  - Action: Check for slow queries in pg_stat_activity

---

## 📊 Viewing Alerts

### In Prometheus
1. Navigate to: http://YOUR_IP:9090
2. Click "Alerts" in top menu
3. See alert status:
   - **Green**: All OK
   - **Yellow**: Pending (condition met, waiting for duration)
   - **Red**: Firing (alert active)

### In Grafana
1. Import Dashboard ID: **15398** (Prometheus Alert Overview)
2. Or create custom dashboard with alert panels
3. View alert history and trends

---

## 🔔 Alert Levels

| Severity | Color | Response Time | Action |
|----------|-------|---------------|--------|
| **Info** | Blue | Monitor | Informational, no action needed |
| **Warning** | Yellow | 30 minutes | Investigate and plan |
| **Critical** | Red | Immediate | Take action now |

---

## 🛠️ Troubleshooting Common Alerts

### High CPU Usage
```bash
# Check top processes
top -n 1

# Check Odoo workers
docker compose logs odoo --tail 50

# Restart if needed
docker compose restart odoo
```

### Low Disk Space
```bash
# Check disk usage
df -h

# Find large files
du -sh /* | sort -h

# Clean Docker
docker system prune -af

# Clean logs
sudo journalctl --vacuum-time=7d
```

### PostgreSQL Issues
```bash
# Check database status
docker compose logs db --tail 50

# Check connections
docker compose exec db psql -U odoo -c "SELECT count(*) FROM pg_stat_activity;"

# Run VACUUM
docker compose exec db psql -U odoo -c "VACUUM ANALYZE;"
```

### High Memory Usage
```bash
# Check memory
free -h

# Check container memory
docker stats

# Restart containers
docker compose restart
```

---

## 📈 Alert Thresholds Explained

| Alert | Warning | Critical | Reasoning |
|-------|---------|----------|-----------|
| CPU | 80% | 95% | Leave headroom for spikes |
| Memory | 85% | 95% | Prevent OOM killer |
| Disk | 20% | 10% | Time to act before full |
| DB Cache | 90% | - | Optimal performance threshold |
| Connections | 80 | - | Default max_connections is 100 |

---

## 🔄 Customizing Alerts

### Adjust Thresholds
Edit alert files in: `/home/ubuntu/monitoring/prometheus/alerts/`

Example - Change CPU threshold:
```yaml
- alert: HighCPUUsage
  expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 70  # Changed from 80
```

### Reload Prometheus
```bash
docker compose restart prometheus
```

---

## 📧 Future: Add Alertmanager (Email/Slack Notifications)

To receive notifications, add Alertmanager:

```yaml
# docker-compose.yml
  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager:/etc/alertmanager
```

Configure notifications in `alertmanager.yml`:
- Email
- Slack
- PagerDuty
- Discord
- Telegram

---

## 📝 Testing Alerts

### Test CPU Alert
```bash
# Stress CPU for 5 minutes
stress --cpu 8 --timeout 300s
```

### Test Disk Alert
```bash
# Create large file
dd if=/dev/zero of=/tmp/testfile bs=1G count=5
# Clean up
rm /tmp/testfile
```

### Test Memory Alert
```bash
# Use stress tool
stress --vm 1 --vm-bytes 1G --timeout 300s
```

---

## 🎯 Best Practices

1. **Review alerts weekly** - Adjust thresholds based on patterns
2. **Don't ignore warnings** - They're early indicators
3. **Document actions** - Keep runbooks for each alert
4. **Test regularly** - Ensure alerts actually fire
5. **Tune thresholds** - Reduce false positives
6. **Monitor alert fatigue** - Too many alerts = ignored alerts

---

## 📚 Resources

- Prometheus Alerting: https://prometheus.io/docs/alerting/latest/
- PromQL Queries: https://prometheus.io/docs/prometheus/latest/querying/basics/
- Grafana Alerts: https://grafana.com/docs/grafana/latest/alerting/

---

**Last Updated**: 2025-11-11
**Version**: 1.0
