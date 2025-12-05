# n8n Workflow Setup Guide

## Prerequisites

- n8n installed and running
- Stock Screener Agent API server running
- (Optional) Gmail account for email notifications
- (Optional) Google Sheets for result storage

## Installation

### 1. Install n8n

```bash
npm install n8n -g
```

### 2. Start n8n

```bash
n8n start
```

n8n will be available at `http://localhost:5678`

## Workflow Setup

### Workflow 1: Webhook-Based Stock Screening

**Purpose**: On-demand stock screening via webhook

**File**: `src/workflows/stock_screener_workflow.json`

#### Import Steps:

1. Open n8n at `http://localhost:5678`
2. Click "Workflows" → "Import from File"
3. Select `src/workflows/stock_screener_workflow.json`
4. Click "Import"

#### Configuration:

1. **Webhook Trigger**:
   - Path: `/stock-screener` (already configured)
   - Response mode: "Response Node"

2. **HTTP Request Node** ("Call Screener API"):
   - URL: Update to your API server URL
   - Default: `http://localhost:5000/api/screen`
   - If running on different host, change accordingly

3. **Activate the workflow**

#### Testing:

```bash
curl -X POST http://localhost:5678/webhook/stock-screener \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "MSFT", "GOOGL", "NVDA", "AMD"]
  }'
```

### Workflow 2: Scheduled Daily Screening

**Purpose**: Automated daily stock screening with notifications

**File**: `src/workflows/scheduled_screening.json`

#### Import Steps:

Same as Workflow 1, but import `scheduled_screening.json`

#### Configuration:

1. **Schedule Trigger**:
   - Cron Expression: `0 9 * * 1-5` (9 AM weekdays)
   - Timezone: Update to your timezone
   - Default: America/New_York

2. **Define Stock Universe** (Function Node):
   - Edit the `stockUniverse` array with your preferred symbols
   - Current defaults: Major tech and growth stocks

3. **HTTP Request Node**:
   - URL: Update to your API server URL
   - Timeout: 600000 (10 minutes for large batches)

4. **Email Send Node** (Optional):
   - Enable the node (currently disabled)
   - Configure your SMTP settings:
     - From Email
     - To Email
     - SMTP credentials
   - Or use Gmail/Outlook integration

5. **Google Sheets Node** (Optional):
   - Enable the node (currently disabled)
   - Authenticate with Google
   - Create a spreadsheet
   - Update `fileId` with your spreadsheet ID

6. **Activate the workflow**

## Workflow Customization

### Change Stock Universe

Edit the "Define Stock Universe" function node:

```javascript
const stockUniverse = [
  'YOUR', 'CUSTOM', 'SYMBOLS', 'HERE'
];
```

### Add Slack Notifications

1. Add "Slack" node after "Format Results"
2. Connect it in the workflow
3. Configure:
   - Workspace: Your Slack workspace
   - Channel: #stock-alerts
   - Message: Use `{{ $json }}` to access results

Example message:
```
🚀 Stock Screening Results

📊 Analyzed: {{ $json.total_analyzed }} stocks
✅ Qualified: {{ $json.qualified_count }}

🏆 Top Pick: {{ $json.best_pick.symbol }}
Score: {{ $json.best_pick.score }}
```

### Add Discord Webhook

1. Create a Discord webhook in your server
2. Add "HTTP Request" node
3. Configure:
   - Method: POST
   - URL: Your Discord webhook URL
   - Body:
   ```json
   {
     "content": "Stock Screening Complete!",
     "embeds": [{
       "title": "Top Picks",
       "description": "{{ $json.summary }}"
     }]
   }
   ```

### Save to Database

1. Add "Postgres/MySQL/MongoDB" node
2. Connect after "Format Results"
3. Configure database connection
4. Insert screening results

Example SQL:
```sql
INSERT INTO screening_results 
(date, total_analyzed, qualified_count, top_pick)
VALUES (
  '{{ $json.screening_date }}',
  {{ $json.total_analyzed }},
  {{ $json.qualified_count }},
  '{{ $json.best_pick.symbol }}'
)
```

## Advanced Configurations

### Multiple Screening Strategies

Create separate workflows for different strategies:

**Growth Strategy**:
- High revenue/earnings growth
- Higher P/E acceptable

**Value Strategy**:
- Lower P/E required
- Strong cash flow focus

**Momentum Strategy**:
- Price near 52-week high
- Strong analyst ratings

### Conditional Notifications

Add an "IF" node to send alerts only when:
- Qualified stocks > threshold
- Top pick score > 80
- New stocks appear in top picks

### Results Comparison

1. Fetch previous results from database/sheets
2. Compare with current results
3. Highlight new opportunities
4. Track performance over time

## Monitoring

### Check Workflow Executions

1. Go to "Executions" in n8n
2. View successful/failed runs
3. Debug any errors

### Common Issues

**Workflow fails at API call**:
- Check API server is running
- Verify URL is correct
- Check timeout settings

**Email not sending**:
- Verify SMTP credentials
- Check spam folder
- Test email settings

**Schedule not triggering**:
- Verify cron expression
- Check timezone settings
- Ensure workflow is active

## Best Practices

1. **Test First**: Use webhook workflow to test before scheduling
2. **Start Small**: Begin with small stock universe
3. **Monitor Costs**: Watch OpenAI API usage
4. **Rate Limits**: Respect API rate limits
5. **Error Handling**: Add retry logic for failed requests
6. **Logging**: Save execution logs for debugging

## Example Workflows

### Morning Routine
```
6:00 AM - Fetch pre-market data
7:00 AM - Run screening
8:00 AM - Send email digest
9:30 AM - Market opens (use results)
```

### End-of-Day Analysis
```
4:00 PM - Market closes
4:30 PM - Fetch final prices
5:00 PM - Run screening
5:30 PM - Generate report
```

### Weekly Deep Dive
```
Saturday 10:00 AM - Screen large universe (100+ stocks)
Compare with previous week
Identify trends
Generate detailed report
```

## Resources

- [n8n Documentation](https://docs.n8n.io/)
- [n8n Community](https://community.n8n.io/)
- [Workflow Templates](https://n8n.io/workflows)

## Support

For workflow-specific issues, check:
1. n8n execution logs
2. API server logs
3. Network connectivity
4. API credentials
