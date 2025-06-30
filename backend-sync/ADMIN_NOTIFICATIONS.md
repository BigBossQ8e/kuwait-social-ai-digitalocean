# Admin Notification System Configuration

The Kuwait Social AI platform includes a comprehensive admin notification system that alerts administrators when critical failures occur.

## Supported Notification Channels

### 1. Email Notifications
Send alerts via SMTP email to configured admin addresses.

**Environment Variables:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ADMIN_EMAILS=admin1@example.com,admin2@example.com
```

### 2. Webhook Notifications (Slack/Discord)
Send alerts to webhook URLs compatible with Slack, Discord, or custom endpoints.

**Environment Variables:**
```bash
ADMIN_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 3. Telegram Notifications
Send alerts to a Telegram chat via bot.

**Environment Variables:**
```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-chat-id
```

## Alert Priority Levels

- **CRITICAL**: System-wide failures requiring immediate attention
- **HIGH**: Service failures affecting functionality
- **MEDIUM**: Performance issues or degraded service
- **LOW**: Informational alerts

## Rate Limiting

To prevent alert spam, the system implements rate limiting:
- Same alerts are only sent once per 30 minutes
- All alerts are logged to `logs/critical_alerts.log`

## Current Alert Triggers

1. **Prayer Times Service**
   - Triggered when all prayer time APIs fail 3+ times consecutively
   - Falls back to cached data with admin notification

2. **Translation Service**
   - Logged when translation fails but doesn't trigger alerts (graceful degradation)

3. **Content Generation**
   - Critical errors in AI content generation trigger HIGH priority alerts

## Testing Notifications

To test your notification configuration:

```python
from services.admin_notification_service import get_notification_service

# Test all configured channels
service = get_notification_service()
results = service.test_notifications()
print(f"Test results: {results}")
```

## Example Alert

When a critical failure occurs, administrators receive:

**Email Format:**
```
Subject: [CRITICAL] Kuwait Social AI Alert: Prayer Time API Failure

Service: PrayerTimesService
Time: 2024-01-15 14:30:45 UTC

Alert Details:
CRITICAL: All prayer time APIs have failed 3 times in a row.

Affected services:
- Aladhan
- Islamic Finder

The system is currently using cached or fallback prayer times.
Please investigate the API connectivity issues.

Time: 2024-01-15 17:30:45 Kuwait Time
```

**Slack/Discord Format:**
- Color-coded alerts (red for CRITICAL, orange for HIGH)
- Formatted with service name, timestamp, and details
- Markdown support for better readability

**Telegram Format:**
- Emoji indicators (🚨 for CRITICAL, ⚠️ for HIGH)
- Markdown formatting
- Inline code blocks for details

## Adding New Alert Triggers

To add alerts to your service:

```python
from services.admin_notification_service import send_critical_alert

# In your service code
if critical_failure_detected:
    send_critical_alert(
        subject="Database Connection Failed",
        message="Unable to connect to database after 5 retry attempts",
        service="DatabaseService",
        priority="CRITICAL"
    )
```

## Security Considerations

1. **Never commit credentials** - Use environment variables
2. **Use app-specific passwords** for email services
3. **Restrict webhook URLs** to trusted sources
4. **Secure Telegram bot** - Keep token private

## Monitoring

All alerts are logged to:
- `logs/critical_alerts.log` - JSON format for parsing
- `logs/kuwait-social-ai.log` - General application logs

Regular monitoring of these logs helps identify patterns and prevent issues.