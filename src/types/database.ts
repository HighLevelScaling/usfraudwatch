export interface Story {
  id: string;
  title: string;
  source_url: string;
  source_name: string;
  published_at: string | null;
  ingested_at: string;
  summary: string | null;
  fraud_type: string | null;
  entities: StoryEntities | null;
  state: string | null;
  city: string | null;
  importance_score: number;
  status: 'new' | 'reviewed' | 'published' | 'rejected';
  reviewed_at: string | null;
  notes: string | null;
}

export interface StoryEntities {
  defendants?: string[];
  organizations?: string[];
  dollar_amounts?: string[];
  charges?: string[];
}

export interface Article {
  id: string;
  title: string;
  slug: string;
  content: string;
  excerpt: string | null;
  status: 'draft' | 'published';
  published_at: string | null;
  meta_description: string | null;
  source_story_ids: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface Subscriber {
  id: string;
  email: string;
  tier: 'free' | 'patriot' | 'watchdog' | 'founder';
  interested_states: string[] | null;
  email_frequency: 'daily' | 'weekly';
  subscribed_at: string;
  unsubscribed_at: string | null;
}

export interface FoiaRequest {
  id: string;
  agency: string;
  topic: string;
  request_text: string | null;
  submitted_at: string | null;
  expected_response: string | null;
  status: 'draft' | 'submitted' | 'received' | 'denied' | 'partial';
  response_summary: string | null;
  documents_received: number | null;
  created_at: string;
}

export type FraudType =
  | 'healthcare'
  | 'financial'
  | 'government'
  | 'tax'
  | 'wire'
  | 'corruption'
  | 'welfare'
  | 'securities'
  | 'insurance'
  | 'other';

export const FRAUD_TYPE_LABELS: Record<FraudType, string> = {
  healthcare: '🏥 Healthcare Fraud',
  financial: '💰 Financial Fraud',
  government: '🏛️ Government Fraud',
  tax: '📋 Tax Fraud',
  wire: '📡 Wire Fraud',
  corruption: '⚖️ Public Corruption',
  welfare: '📑 Welfare Fraud',
  securities: '📈 Securities Fraud',
  insurance: '🛡️ Insurance Fraud',
  other: '📁 Other',
};

export const STATE_NAMES: Record<string, string> = {
  MN: 'Minnesota',
  CA: 'California',
  TX: 'Texas',
  NY: 'New York',
  FL: 'Florida',
  IL: 'Illinois',
  PA: 'Pennsylvania',
  OH: 'Ohio',
  GA: 'Georgia',
  NC: 'North Carolina',
};
