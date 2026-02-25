-- US Fraud Watch Database Schema
-- Run this in Supabase SQL Editor to set up your database

-- ============================================
-- STORIES TABLE (Raw ingested fraud stories)
-- ============================================
CREATE TABLE IF NOT EXISTS stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Core content
    title TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    source_name TEXT NOT NULL,
    published_at TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ DEFAULT NOW(),

    -- AI-extracted fields
    summary TEXT,
    fraud_type TEXT,
    entities JSONB DEFAULT '{}',

    -- Geography
    state TEXT,
    city TEXT,

    -- Scoring (0-100)
    importance_score INTEGER DEFAULT 50 CHECK (importance_score >= 0 AND importance_score <= 100),

    -- Editorial workflow
    status TEXT DEFAULT 'new' CHECK (status IN ('new', 'reviewed', 'published', 'rejected')),
    reviewed_at TIMESTAMPTZ,
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_stories_state ON stories(state);
CREATE INDEX IF NOT EXISTS idx_stories_fraud_type ON stories(fraud_type);
CREATE INDEX IF NOT EXISTS idx_stories_importance ON stories(importance_score DESC);
CREATE INDEX IF NOT EXISTS idx_stories_published ON stories(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_stories_status ON stories(status);
CREATE INDEX IF NOT EXISTS idx_stories_source_name ON stories(source_name);

-- Full text search index
CREATE INDEX IF NOT EXISTS idx_stories_title_search ON stories USING gin(to_tsvector('english', title));

-- ============================================
-- ARTICLES TABLE (Your written content)
-- ============================================
CREATE TABLE IF NOT EXISTS articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Content
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    excerpt TEXT,

    -- Publishing
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    published_at TIMESTAMPTZ,

    -- SEO
    meta_description TEXT,

    -- Linked source stories
    source_story_ids UUID[],

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug);
CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at DESC);

-- ============================================
-- SUBSCRIBERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,

    -- Subscription tier
    tier TEXT DEFAULT 'free' CHECK (tier IN ('free', 'patriot', 'watchdog', 'founder')),

    -- Preferences
    interested_states TEXT[],
    email_frequency TEXT DEFAULT 'daily' CHECK (email_frequency IN ('daily', 'weekly', 'none')),

    -- Tracking
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ,
    last_email_sent TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);
CREATE INDEX IF NOT EXISTS idx_subscribers_tier ON subscribers(tier);
CREATE INDEX IF NOT EXISTS idx_subscribers_frequency ON subscribers(email_frequency);

-- ============================================
-- FOIA REQUESTS TRACKER
-- ============================================
CREATE TABLE IF NOT EXISTS foia_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Request details
    agency TEXT NOT NULL,
    agency_type TEXT CHECK (agency_type IN ('federal', 'state', 'local')),
    topic TEXT NOT NULL,
    request_text TEXT,

    -- Tracking
    submitted_at DATE,
    expected_response DATE,
    actual_response DATE,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'acknowledged', 'processing', 'received', 'denied', 'partial', 'appealed')),

    -- Response
    response_summary TEXT,
    documents_received INTEGER DEFAULT 0,
    document_urls TEXT[],

    -- Linked content
    resulting_article_ids UUID[],

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_foia_status ON foia_requests(status);
CREATE INDEX IF NOT EXISTS idx_foia_agency ON foia_requests(agency);

-- ============================================
-- ANALYTICS / PAGE VIEWS (Optional)
-- ============================================
CREATE TABLE IF NOT EXISTS page_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    path TEXT NOT NULL,
    story_id UUID REFERENCES stories(id) ON DELETE SET NULL,
    article_id UUID REFERENCES articles(id) ON DELETE SET NULL,
    referrer TEXT,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_page_views_path ON page_views(path);
CREATE INDEX IF NOT EXISTS idx_page_views_created ON page_views(created_at DESC);

-- ============================================
-- ROW LEVEL SECURITY POLICIES
-- ============================================

-- Enable RLS on all tables
ALTER TABLE stories ENABLE ROW LEVEL SECURITY;
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE foia_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE page_views ENABLE ROW LEVEL SECURITY;

-- Public read access for published content
CREATE POLICY "Public can read all stories" ON stories
    FOR SELECT USING (true);

CREATE POLICY "Public can read published articles" ON articles
    FOR SELECT USING (status = 'published');

-- Service role can do everything (for n8n automation)
CREATE POLICY "Service role full access to stories" ON stories
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to articles" ON articles
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to subscribers" ON subscribers
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to foia_requests" ON foia_requests
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to page_views" ON page_views
    FOR ALL USING (auth.role() = 'service_role');

-- Allow anonymous inserts to subscribers (for newsletter signup)
CREATE POLICY "Anyone can subscribe" ON subscribers
    FOR INSERT WITH CHECK (true);

-- Allow anonymous inserts to page_views (for analytics)
CREATE POLICY "Anyone can log page views" ON page_views
    FOR INSERT WITH CHECK (true);

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables with updated_at
CREATE TRIGGER update_stories_updated_at
    BEFORE UPDATE ON stories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_articles_updated_at
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_foia_updated_at
    BEFORE UPDATE ON foia_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to get stories by state with importance sorting
CREATE OR REPLACE FUNCTION get_state_stories(target_state TEXT, limit_count INTEGER DEFAULT 10)
RETURNS SETOF stories AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM stories
    WHERE state = target_state
    ORDER BY importance_score DESC, published_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get daily digest stories
CREATE OR REPLACE FUNCTION get_daily_digest(hours_back INTEGER DEFAULT 24, limit_count INTEGER DEFAULT 20)
RETURNS SETOF stories AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM stories
    WHERE ingested_at >= NOW() - (hours_back || ' hours')::INTERVAL
    ORDER BY importance_score DESC, published_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- SAMPLE DATA (Optional - Remove in production)
-- ============================================

-- Uncomment below to insert sample data for testing

/*
INSERT INTO stories (title, source_url, source_name, published_at, summary, fraud_type, state, importance_score, status) VALUES
('Minnesota Man Sentenced to 10 Years for $5.2 Million COVID Relief Fraud', 'https://www.justice.gov/usao-mn/pr/minnesota-man-sentenced-covid-fraud', 'DOJ', NOW() - INTERVAL '2 hours', 'A Minnesota man was sentenced to 120 months in federal prison for fraudulently obtaining over $5.2 million in COVID-19 relief funds through fake businesses.', 'government', 'MN', 85, 'new'),
('California Healthcare Executive Charged in $100 Million Medicare Fraud Scheme', 'https://www.justice.gov/usao-cdca/pr/healthcare-exec-charged', 'DOJ', NOW() - INTERVAL '5 hours', 'Federal prosecutors charged a Southern California healthcare executive with orchestrating a $100 million Medicare fraud scheme involving phantom patients.', 'healthcare', 'CA', 92, 'new'),
('SEC Charges Investment Adviser with $25 Million Ponzi Scheme', 'https://www.sec.gov/litigation/litreleases/2024/lr12345.htm', 'SEC', NOW() - INTERVAL '1 day', 'The SEC charged an investment adviser and his firm with running a Ponzi scheme that defrauded investors of approximately $25 million.', 'securities', 'NY', 78, 'new'),
('FBI Arrests Public Official in Minnesota Corruption Probe', 'https://www.fbi.gov/news/press-releases/minnesota-corruption', 'FBI', NOW() - INTERVAL '3 hours', 'FBI agents arrested a county official in Minnesota on charges of accepting bribes in exchange for favorable contract awards.', 'corruption', 'MN', 88, 'new'),
('California State Auditor Finds $50 Million in Wasteful Spending', 'https://www.auditor.ca.gov/reports/2024-001', 'CA State Auditor', NOW() - INTERVAL '12 hours', 'A new audit reveals significant waste and mismanagement in a California state agency, totaling over $50 million in questionable expenditures.', 'government', 'CA', 75, 'new');

INSERT INTO subscribers (email, tier, interested_states, email_frequency) VALUES
('test@example.com', 'free', ARRAY['MN', 'CA'], 'daily');
*/
