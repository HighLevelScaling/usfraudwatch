# US Fraud Watch

Data-driven tracking of fraud, waste, and corruption across America from official government sources.

## Features

- **Automated Ingestion**: n8n workflows monitor DOJ, FBI, SEC, FTC, and state AGs
- **Priority State Coverage**: Special focus on Minnesota and California
- **Real-time Updates**: Stories ingested hourly from official sources
- **Newsletter Subscription**: Daily fraud alerts delivered via email
- **Source Verification**: Every story links to original government documents

## Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **Automation**: n8n workflows
- **Hosting**: Vercel/Cloudflare Pages (free tier)
- **Email**: Resend (free tier: 3K/month)

## Quick Start

### 1. Clone and Install

```bash
cd usfraudwatch
npm install
```

### 2. Set Up Supabase

1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Go to SQL Editor, paste contents of `supabase/schema.sql`, and run
4. Copy API keys from Settings → API

### 3. Configure Environment

```bash
cp .env.example .env.local
```

Edit `.env.local` with your Supabase credentials:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
INGESTION_API_KEY=generate-a-random-string
```

### 4. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 5. Set Up n8n Automation

1. Create account at [n8n.io](https://n8n.io)
2. Import workflows from `n8n-workflows/` folder
3. Add environment variables in n8n:
   - `SITE_URL`: Your deployed URL
   - `INGESTION_API_KEY`: Same as `.env.local`
4. Activate workflows

## Project Structure

```
usfraudwatch/
├── src/
│   ├── app/                    # Next.js pages
│   │   ├── page.tsx           # Homepage
│   │   ├── stories/           # All stories page
│   │   ├── states/            # State-specific pages
│   │   ├── subscribe/         # Newsletter signup
│   │   └── api/               # API routes
│   ├── components/            # React components
│   ├── lib/                   # Utilities & Supabase client
│   └── types/                 # TypeScript types
├── supabase/
│   └── schema.sql             # Database schema
├── n8n-workflows/             # Automation workflows
│   ├── 01-federal-fraud-monitor.json
│   ├── 02-state-ag-monitor.json
│   └── README.md
└── .env.example               # Environment template
```

## Data Sources

### Federal
- **DOJ**: justice.gov/news
- **FBI**: fbi.gov/news
- **SEC**: sec.gov/litigation
- **FTC**: ftc.gov/news

### State (Priority)
- **Minnesota AG**: ag.state.mn.us
- **California AG**: oag.ca.gov/news

### Courts
- **CourtListener**: courtlistener.com (free federal court opinions)
- **PACER**: pacer.gov (federal court filings - $0.10/page)

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

Add environment variables in Vercel dashboard.

### Cloudflare Pages

```bash
npm install -g wrangler
npm run build
wrangler pages deploy .next
```

## API Endpoints

### `GET /api/stories`
Fetch stories with optional filters.

Query params:
- `state`: Filter by state (e.g., `MN`, `CA`)
- `type`: Filter by fraud type
- `source`: Filter by source name
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset

### `POST /api/stories`
Add new story (requires `x-api-key` header).

```json
{
  "title": "Story title",
  "source_url": "https://...",
  "source_name": "DOJ",
  "published_at": "2025-01-17T00:00:00Z",
  "summary": "Brief summary",
  "fraud_type": "healthcare",
  "state": "MN",
  "importance_score": 75
}
```

### `POST /api/subscribe`
Subscribe to newsletter.

```json
{
  "email": "user@example.com",
  "interested_states": ["MN", "CA"]
}
```

## Costs

| Service | Free Tier | Paid |
|---------|-----------|------|
| Supabase | 500MB, 50K rows | $25/mo |
| n8n Cloud | 5 workflows | $20/mo |
| Vercel | 100GB bandwidth | $20/mo |
| Resend | 3K emails/month | $20/mo |
| **Total** | **$0/month** | ~$85/mo |

## Adding More Sources

### Add RSS Feed to n8n

1. Open Federal Fraud Monitor workflow
2. Add new "RSS Feed Read" node
3. Connect to "Merge All Feeds" node
4. Update "Process & Classify" code to detect new source

### Add State AG

1. Check if state has RSS feed (search "[state] attorney general rss")
2. If RSS: Add RSS Read node
3. If no RSS: Add HTTP Request node + HTML Extract node
4. Process and save to database

## License

MIT

## Disclaimer

This platform aggregates publicly available government information for educational and journalistic purposes. We do not make legal determinations about guilt or innocence. All information is sourced from official government press releases and court documents. We link to primary sources for verification.
