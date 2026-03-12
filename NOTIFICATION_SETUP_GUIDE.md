# Alert Notifications Setup Guide

## 🎯 Overview

Alertmanager is now **running** and **receiving alerts from Prometheus**!

Currently, alerts go to a webhook (placeholder). Now you need to configure **real notifications**.

---

## 📧 Where Alerts Go Now:

**Access Alertmanager UI:**
- URL: http://YOUR_IP:9093
- Shows active alerts
- Shows silenced alerts
- Shows alert history

**Config file:** `/home/ubuntu/monitoring/alertmanager/alertmanager.yml`

---

## 🔔 Setup Notification Channels

Choose ONE or MORE methods below:

### Option 1: EMAIL Notifications

**1. Edit Alertmanager config:**
```bash
nano /home/ubuntu/monitoring/alertmanager/alertmanager.yml
```

**2. Find the `critical-receiver` section and uncomment email:**
```yaml
  - name: 'critical-receiver'
    email_configs:
      - to: 'your-email@example.com'
        from: 'alertmanager@yourdomain.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'your-email@gmail.com'
        auth_password: 'your-app-password'  # NOT your regular password!
        headers:
          Subject: '🚨 CRITICAL ALERT: {{ .GroupLabels.alertname }}'
```

**3. For Gmail, create App Password:**
- Go to: https://myaccount.google.com/apppasswords
- Generate app password
- Use that instead of your regular password

**4. Restart Alertmanager:**
```bash
docker compose restart alertmanager
```

---

### Option 2: SLACK Notifications

**1. Create Slack Incoming Webhook:**
- Go to: https://api.slack.com/messaging/webhooks
- Create new webhook
- Copy webhook URL

**2. Edit config, uncomment slack section:**
```yaml
  - name: 'critical-receiver'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
        title: '🚨 Critical Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ .Annotations.description }}\n{{ end }}'
```

**3. Restart:**
```bash
docker compose restart alertmanager
```

---

### Option 3: DISCORD Notifications

**1. Create Discord Webhook:**
- Open Discord channel settings
- Integrations → Webhooks → New Webhook
- Copy webhook URL

**2. Edit config:**
```yaml
  - name: 'critical-receiver'
    webhook_configs:
      - url: 'https://discord.com/api/webhooks/YOUR/WEBHOOK/URL'
        send_resolved: true
```

**Use Discord-specific format:**
```yaml
  - name: 'critical-receiver'
    webhook_configs:
      - url: 'https://discord.com/api/webhooks/123456/abcdef'
        send_resolved: true
        http_config:
          headers:
            Content-Type: 'application/json'
```

**3. Restart:**
```bash
docker compose restart alertmanager
```

---

### Option 4: TELEGRAM Notifications

**1. Create Telegram Bot:**
```bash
# Talk to @BotFather on Telegram
# Send: /newbot
# Follow instructions
# You'll get a BOT_TOKEN
```

**2. Get your Chat ID:**
```bash
# Send a message to your bot
# Then visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
# Find "chat":{"id":123456789}
```

**3. Edit config:**
```yaml
  - name: 'critical-receiver'
    telegram_configs:
      - bot_token: 'YOUR_BOT_TOKEN'
        chat_id: 123456789
        message: '🚨 *CRITICAL ALERT*\n{{ range .Alerts }}{{ .Annotations.summary }}\n{{ end }}'
        parse_mode: 'Markdown'
```

**4. Restart:**
```bash
docker compose restart alertmanager
```

---

## 🧪 Test Notifications

### Method 1: Trigger Real Alert
```bash
# Fill disk space to trigger alert
dd if=/dev/zero of=/tmp/testfile bs=1M count=3000

# Wait 5 minutes, check Alertmanager
# Then delete: rm /tmp/testfile
```

### Method 2: Send Test Alert
```bash
# Send test alert to Alertmanager
curl -X POST http://localhost:9093/api/v1/alerts -d '[
  {
    "labels": {
      "alertname": "TestAlert",
      "severity": "critical"
    },
    "annotations": {
      "summary": "This is a test alert",
      "description": "Testing notification system"
    }
  }
]'
```

---

## 📊 View Alerts

**Alertmanager UI:** http://YOUR_IP:9093
- Shows active alerts
- Silence alerts
- See notification history

**Prometheus Alerts:** http://YOUR_IP:9090/alerts
- Shows alert rules
- Alert status (pending/firing)

**Grafana:** Import Dashboard 9578 (Alertmanager)
- Visual alert overview

---

## ⚙️ Alert Routing Logic

Current setup (in alertmanager.yml):

```
Alert Fired
    │
    ├─ severity: critical  →  Immediate notification
    │                         Repeat every 5 minutes
    │
    ├─ severity: warning   →  Notification
    │                         Repeat every 1 hour
    │
    └─ severity: info      →  Notification
                              Repeat every 24 hours
```

---

## 🔕 Silence Alerts

Go to Alertmanager UI: http://YOUR_IP:9093

1. Click "Silence"
2. Add matcher (alertname, severity, etc.)
3. Set duration
4. Add comment
5. Click "Create"

**Example:** Silence disk alerts during maintenance:
```
Matcher: alertname="HighDiskUsage"
Duration: 2h
Comment: "Maintenance window - cleaning disk"
```

---

## 📝 Example Configurations

### Full Gmail Example:
```yaml
receivers:
  - name: 'critical-receiver'
    email_configs:
      - to: 'devops@company.com'
        from: 'odoo-alerts@company.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'odoo-alerts@company.com'
        auth_password: 'abcd efgh ijkl mnop'  # App password
        headers:
          Subject: '🚨 [ODOO] {{ .GroupLabels.alertname }}'
        html: |
          <h2>{{ .GroupLabels.alertname }}</h2>
          {{ range .Alerts }}
          <p><strong>Summary:</strong> {{ .Annotations.summary }}</p>
          <p><strong>Description:</strong> {{ .Annotations.description }}</p>
          <hr>
          {{ end }}
```

### Full Slack Example:
```yaml
receivers:
  - name: 'critical-receiver'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX'
        channel: '#production-alerts'
        username: 'Odoo Alertmanager'
        icon_emoji: ':fire:'
        title: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
        text: |
          {{ range .Alerts }}
          *Alert:* {{ .Labels.alertname }}
          *Severity:* {{ .Labels.severity }}
          *Description:* {{ .Annotations.description }}
          {{ end }}
        send_resolved: true
```

---

## 🚨 Troubleshooting

### Notifications not sending?

1. **Check Alertmanager logs:**
```bash
docker compose logs alertmanager -f
```

2. **Check Alertmanager config:**
```bash
docker compose exec alertmanager amtool check-config /etc/alertmanager/alertmanager.yml
```

3. **Test connectivity:**
```bash
# For Gmail
telnet smtp.gmail.com 587

# For webhook
curl -X POST YOUR_WEBHOOK_URL -d '{"test":"message"}'
```

4. **Verify alerts are firing:**
- Go to: http://YOUR_IP:9090/alerts
- Should see red "FIRING" alerts

5. **Check Alertmanager UI:**
- Go to: http://YOUR_IP:9093
- Should see alerts listed

---

## 📚 Additional Resources

- Alertmanager Config: https://prometheus.io/docs/alerting/latest/configuration/
- Notification Templates: https://prometheus.io/docs/alerting/latest/notifications/
- Slack Integration: https://api.slack.com/messaging/webhooks
- Discord Webhooks: https://discord.com/developers/docs/resources/webhook

---

**Last Updated:** 2025-11-11
**Version:** 1.0
