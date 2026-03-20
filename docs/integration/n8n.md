# n8n Integration

Connect Automated Calling to n8n workflows for real-world business automation.

## What is n8n?

n8n is a low-code workflow automation platform that connects your voice commands to business applications:
- **CRM**: Update contacts, log calls
- **Slack**: Send messages
- **Email**: Send notifications
- **Databases**: Query/update records
- **APIs**: Call any REST endpoint

## Setup

### 1. Install & Run n8n

```bash
npm install -g n8n
n8n start

# Runs on http://localhost:5678
```

Or use Docker:
```bash
docker run -it -p 5678:5678 n8nio/n8n
```

### 2. Create Webhook Trigger

1. Open n8n: http://localhost:5678
2. Create new workflow
3. Add node: **Webhook**
4. Configure:
   - **HTTP Method**: POST
   - **Path**: `/voice-agent` (or any path)
5. Copy webhook URL

Example URL:
```
http://localhost:5678/webhook/your-unique-id
```

Or with n8n cloud:
```
https://your-instance.n8n.cloud/webhook/your-unique-id
```

### 3. Configure Automated Calling

Set webhook URL in `.env`:

```env
N8N_WEBHOOK_URL=http://localhost:5678/webhook/your-unique-id
```

Or for n8n cloud:
```env
N8N_WEBHOOK_URL=https://your-instance.n8n.cloud/webhook/your-unique-id
```

## Webhook Payload

Each transcribed sentence sends a POST request to your webhook:

```json
{
  "user_input": "What's the weather?",
  "timestamp": "2026-03-20T10:30:00Z",
  "confidence": 0.98
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `user_input` | string | The transcribed user speech |
| `timestamp` | ISO 8601 | When the transcription occurred |
| `confidence` | 0.0-1.0 | Transcription confidence (from Whisper) |

## Example Workflows

### 1. Slack Notification

Send transcribed commands to Slack:

```
Webhook → Slack (Send Message)
           └─ Channel: #voice-commands
           └─ Message: "User said: {{user_input}}"
```

**Configuration**:
1. Add Slack node after Webhook
2. Authenticate with Slack workspace
3. Select channel
4. Message template: `🎤 Voice Command: {{ $node.Webhook.json.user_input }}`

### 2. CRM Integration (HubSpot)

Log calls and create notes:

```
Webhook → HubSpot (Create Note)
           └─ Contact ID: {{contact_id}}
           └─ Note: "Called, said: {{user_input}}"
```

### 3. Database Query

Store voice commands in database:

```
Webhook → PostgreSQL (Insert)
           └─ Table: voice_commands
           └─ user_input: {{user_input}}
           └─ timestamp: {{timestamp}}
           └─ confidence: {{confidence}}
```

### 4. Conditional Logic

Different responses based on keywords:

```
Webhook → IF (user_input contains "weather")
             → Weather API
          ELSE IF (user_input contains "schedule")
             → Calendar API
          ELSE
             → Slack (unhandled command)
```

## Advanced Configuration

### Rate Limiting

Prevent webhook spam:

```
Webhook → Wait (1 second)
       → Deduplication (check last command within 5s)
       → Process...
```

### Logging

Send to external logging service:

```
Webhook → Datadog (Log)
       └─ Message: {{user_input}}
       └─ Confidence: {{confidence}}
```

### Error Handling

Graceful error responses:

```
Webhook → Try/Catch
           ├─ Success → HTTP Response 200
           └─ Error → HTTP Response 500 + Log
```

## Security

### HTTPS (Production)

Use n8n cloud or reverse proxy for HTTPS:

```env
# n8n Cloud (recommended for production)
N8N_WEBHOOK_URL=https://your-instance.n8n.cloud/webhook/...

# Or self-hosted with nginx reverse proxy
N8N_WEBHOOK_URL=https://voice-api.yourdomain.com/webhook/...
```

### Authentication

Add API key requirement in n8n:

**Node Setup**:
1. Webhook node → Authentication
2. Add header: `Authorization: Bearer YOUR_SECRET_KEY`

**Automated Calling** (`src/integrations/n8n_client.py`):
```python
headers = {
    "Authorization": f"Bearer {API_KEY}"
}
```

### Input Validation

Verify webhook source:

```
Webhook → Check Request
          ├─ Source IP in whitelist?
          ├─ Signature valid?
          └─ Rate limit exceeded?
```

## Troubleshooting

### "Webhook not reachable" error

1. **Check n8n is running**
   ```bash
   curl http://localhost:5678
   ```

2. **Check webhook URL in .env**
   ```env
   N8N_WEBHOOK_URL=http://localhost:5678/webhook/your-id
   ```

3. **Check firewall**
   - Port 5678 open?
   - Firewall blocking?

### Webhook not receiving calls

1. **Check n8n webhook path**
   - Copy exact webhook URL from n8n
   - No typos in `.env`

2. **Check Automated Calling logs**
   ```bash
   grep "webhook" automated_calling.log
   ```

3. **Test webhook manually**
   ```bash
   curl -X POST http://localhost:5678/webhook/your-id \
     -H "Content-Type: application/json" \
     -d '{"user_input":"test","timestamp":"2026-03-20T10:30:00Z","confidence":0.95}'
   ```

### Slow webhook responses

1. **Add timeout handling**
   ```
   n8n → Set timeout to 5 seconds
      → If timeout, continue (don't wait)
   ```

2. **Use async processing**
   ```
   n8n → Queue workflow
      → Process in background
      → Respond immediately (don't wait)
   ```

### High webhook latency (>5s total)

1. **Reduce n8n workflow complexity**
   - Remove unnecessary API calls
   - Optimize database queries

2. **Run n8n locally**
   - Cloud n8n has latency
   - Local execution is faster

3. **Disable webhook temporarily**
   ```env
   N8N_WEBHOOK_URL=        # Empty = disabled
   ```

## Monitoring

### Check Webhook Calls

In n8n:
1. Open your workflow
2. Click node execution logs
3. See all received payloads

### Log Webhook Events

Add logging to workflow:

```
Webhook → Log to File
       → Log to Datadog
       → Log to CloudWatch
```

## Best Practices

1. **Keep workflow fast** (<3s response time)
2. **Add error handling** (Try/Catch nodes)
3. **Log all calls** (for debugging)
4. **Use HTTPS in production** (security)
5. **Test with curl first** (before running agent)
6. **Monitor webhook metrics** (rate, errors, latency)

## Example: Complete Contact Logging Workflow

```
1. Webhook (receive voice input)
   ↓
2. Check Confidence (> 0.9?)
   ├─ Low confidence → End
   ├─ High confidence → Continue
   ↓
3. HubSpot Get Contact (by email)
   ↓
4. HubSpot Update Contact
   - Add note: "{{user_input}}"
   - Update last_contacted: {{timestamp}}
   ↓
5. Slack Notification
   - Channel: #sales
   - Message: "New voice note: {{user_input}}"
   ↓
6. HTTP Response (success)
```

---

See [Quick Start](../quickstart.md) for basic setup.
