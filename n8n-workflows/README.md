# n8n Workflows for US Fraud Watch

These workflows automate the ingestion of fraud-related stories from government sources.

## Workflows

### 01-federal-fraud-monitor.json
- **Frequency**: Hourly
- **Sources**: DOJ, FBI, SEC, FTC RSS feeds
- **Function**: Monitors federal agency press releases for fraud-related stories

### 02-state-ag-monitor.json
- **Frequency**: Every 2 hours
- **Sources**: Minnesota AG, California AG
- **Function**: Monitors priority state attorney general announcements

## Setup Instructions

### 1. Create n8n Account
1. Go to [n8n.io](https://n8n.io)
2. Sign up for free cloud account (or self-host)
3. Free tier: 5 workflows, 500 executions/month

### 2. Set Environment Variables

In n8n, go to **Settings → Variables** and add:

| Variable | Description | Example |
|----------|-------------|---------|
| `SITE_URL` | Your deployed site URL | `https://usfraudwatch.com` |
| `INGESTION_API_KEY` | API key for write access | `your-secret-key-here` |
| `ALERT_EMAIL` | Email for new story alerts | `editor@usfraudwatch.com` |

### 3. Import Workflows

1. In n8n, click **Workflows** → **Import from File**
2. Upload each `.json` file from this folder
3. Click **Activate** on each workflow

### 4. Configure Email (Optional)

If using the email alert feature:
1. Go to **Credentials** → **Add Credential**
2. Select your email provider (Gmail, SendGrid, etc.)
3. Connect the credential to the "Send Alert Email" node

## Customization

### Adding More Sources

Edit the workflows to add more RSS feeds:
- DOJ district offices: `https://www.justice.gov/usao-[district]/news/rss`
- Other state AGs: Search for their RSS feeds or press pages
- HHS OIG: `https://oig.hhs.gov/reports-and-publications/`

### Adjusting Fraud Detection

The fraud keyword regex in the filter nodes can be customized:
```regex
fraud|embezzlement|scheme|corruption|bribery|theft|misappropriation|ponzi|kickback|conspiracy|indictment|sentenced|charged|pleaded guilty
```

### Changing Importance Scoring

Edit the "Process & Classify" code node to adjust:
- Dollar amount thresholds
- State priority boosts
- Source priority boosts

## Monitoring

### Check Execution History
1. Go to **Executions** in n8n
2. View success/failure for each run
3. Debug failed executions

### Common Issues

**"Failed to fetch"**: RSS feed URL changed or is down
- Solution: Check if the URL is still valid

**"Unauthorized"**: API key mismatch
- Solution: Verify `INGESTION_API_KEY` matches your `.env.local`

**"Duplicate"**: Story already exists
- This is expected behavior, not an error

## Data Flow

```
RSS Feed → Filter (fraud keywords) → Process (extract entities) → API → Database
```

Each story is deduplicated by `source_url` to prevent duplicates.
