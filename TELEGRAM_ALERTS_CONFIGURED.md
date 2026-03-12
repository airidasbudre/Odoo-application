# ✅ Telegram Notifications Configured!

## 📱 Your Alert Setup

**Telegram Bot**: Odoo Alerts Bot
**Bot Token**: `8549606640:AAFeq8nCCFTngsz_BWwDZLIthEkPZLXffpA`
**Chat ID**: `5033985200`
**Status**: ✅ ACTIVE

---

## 🔔 How It Works

```
Alert Triggered in System
         ↓
Prometheus Detects Issue
         ↓
Alert Rule Fires
         ↓
Prometheus → Alertmanager
         ↓
Alertmanager → Telegram Bot
         ↓
📱 Message Arrives in Your Telegram!
```

---

## ⚙️ Alert Routing

| Severity | Icon | Repeat Interval | Example |
|----------|------|----------------|---------|
| **Critical** | 🚨 | Every 5 minutes | Database down, Disk full |
| **Warning** | ⚠️ | Every 1 hour | High CPU, Low disk space |
| **Info** | ℹ️ | Every 24 hours | Database growing |

---

## 📊 Your 17 Active Alerts

### System Alerts (8):
- HighCPUUsage (>80%)
- CriticalCPUUsage (>95%)
- HighMemoryUsage (>85%)
- CriticalMemoryUsage (>95%)
- HighDiskUsage (<20% free)
- CriticalDiskUsage (<10% free)
- HighDiskIO
- HighSystemLoad

### Database Alerts (6):
- PostgreSQLDown
- HighDatabaseConnections (>80)
- LowCacheHitRatio (<90%)
- HighRollbackRate (>10%)
- DatabaseSizeGrowingRapidly
- HighDeadTuples

### Application Alerts (3):
- OdooApplicationIssue
- HighQueryRate
- PossibleSlowQueries

---

## 🧪 Test Your Notifications

### Method 1: Trigger Real Alert (Safe)
```bash
# Create large file to trigger disk alert
dd if=/dev/zero of=/tmp/testfile bs=1M count=3000

# Wait 5-10 minutes
# You'll receive Telegram notification!

# Clean up
rm /tmp/testfile
```

### Method 2: Manual Test Alert
```bash
curl -X POST http://localhost:9093/api/v2/alerts -H "Content-Type: application/json" -d '[
  {
    "labels": {"alertname": "TestAlert", "severity": "critical"},
    "annotations": {
      "summary": "Test Alert",
      "description": "Testing Telegram notifications"
    }
  }
]'
```

---

## 📍 Where to View Alerts

**Alertmanager UI**: http://YOUR_IP:9093
- See active alerts
- Silence alerts
- View history

**Prometheus Alerts**: http://YOUR_IP:9090/alerts
- See all 17 alert rules
- Check alert status

**Grafana Dashboard**: http://YOUR_IP:3000
- Visual alert overview
- Import Dashboard ID: 15398

---

## 🔕 Silence an Alert

If you need to silence alerts (e.g., during maintenance):

1. Go to: http://YOUR_IP:9093
2. Click "Silence"
3. Add matcher:
   - `alertname="HighDiskUsage"`
4. Duration: `2h`
5. Comment: "Maintenance"
6. Click "Create"

---

## 🎨 Sample Telegram Message

When an alert fires, you'll receive:

```
🚨 TestAlert

Severity: critical
Summary: Test notification from Odoo DevOps
Description: This is a test alert to verify Telegram notifications are working!
Status: firing
```

When resolved:

```
✅ TestAlert

Severity: critical
Summary: Test notification from Odoo DevOps
Description: This is a test alert to verify Telegram notifications are working!
Status: resolved
```

---

## 🛠️ Configuration Files

**Alertmanager Config**:
`/home/ubuntu/monitoring/alertmanager/alertmanager.yml`

**Prometheus Config**:
`/home/ubuntu/monitoring/prometheus/prometheus.yml`

**Alert Rules**:
`/home/ubuntu/monitoring/prometheus/alerts/*.yml`

---

## 📝 What Happens Next?

**Automatically**:
- Prometheus checks metrics every 15 seconds
- Alert rules evaluated every 30 seconds
- If condition met → Alert fires
- Alertmanager routes to Telegram
- You receive notification!

**When Alert Resolves**:
- Prometheus detects condition is OK
- Sends "resolved" to Alertmanager
- You receive ✅ resolved notification

---

## 🚀 Your Complete Stack

| Service | Status | Port | Purpose |
|---------|--------|------|---------|
| Odoo | ✅ | 8069 | ERP Application |
| PostgreSQL | ✅ | 5432 | Database |
| Grafana | ✅ | 3000 | Dashboards |
| Prometheus | ✅ | 9090 | Metrics & Alerts |
| **Alertmanager** | ✅ | 9093 | **Telegram Notifications** |
| Node Exporter | ✅ | 9100 | System Metrics |
| PG Exporter | ✅ | 9187 | DB Metrics |

---

## 🎯 All Set!

Your monitoring system is now **fully configured** with:
- ✅ 17 alert rules monitoring everything
- ✅ Telegram notifications active
- ✅ Automatic alert routing
- ✅ All services running

**You'll receive Telegram messages** when:
- CPU or Memory is high
- Disk space is low
- Database has issues
- System load is high
- Odoo application problems

---

**Last Updated**: 2025-11-11
**Version**: 1.0
**Status**: PRODUCTION READY 🚀
