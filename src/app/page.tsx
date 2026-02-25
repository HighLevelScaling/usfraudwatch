import { supabase } from '@/lib/supabase';
import { Story } from '@/types/database';
import { StoryCard } from '@/components/story-card';
import { NewsletterForm } from '@/components/newsletter-form';
import Link from 'next/link';

// Revalidate every hour
export const revalidate = 3600;

async function getTopStories(): Promise<Story[]> {
  const { data, error } = await supabase
    .from('stories')
    .select('*')
    .order('importance_score', { ascending: false })
    .order('published_at', { ascending: false })
    .limit(10);

  if (error) {
    console.error('Error fetching top stories:', error);
    return [];
  }

  return data || [];
}

async function getStateStories(state: string): Promise<Story[]> {
  const { data, error } = await supabase
    .from('stories')
    .select('*')
    .eq('state', state)
    .order('published_at', { ascending: false })
    .limit(5);

  if (error) {
    console.error(`Error fetching ${state} stories:`, error);
    return [];
  }

  return data || [];
}

async function getRecentStories(): Promise<Story[]> {
  const { data, error } = await supabase
    .from('stories')
    .select('*')
    .order('ingested_at', { ascending: false })
    .limit(5);

  if (error) {
    console.error('Error fetching recent stories:', error);
    return [];
  }

  return data || [];
}

export default async function HomePage() {
  const [topStories, mnStories, caStories, recentStories] = await Promise.all([
    getTopStories(),
    getStateStories('MN'),
    getStateStories('CA'),
    getRecentStories(),
  ]);

  const heroStory = topStories[0];
  const remainingTopStories = topStories.slice(1, 7);

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-slate-900 to-slate-800 text-white py-12">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-8">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Tracking Fraud Across America
            </h1>
            <p className="text-xl text-slate-300 max-w-2xl mx-auto">
              Data-driven monitoring of fraud, waste, and corruption from official
              government sources. Updated hourly.
            </p>
          </div>

          {/* Newsletter CTA */}
          <div className="max-w-xl mx-auto bg-white/10 backdrop-blur rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-3 text-center">
              Get Daily Fraud Alerts
            </h2>
            <NewsletterForm variant="hero" />
          </div>
        </div>
      </section>

      {/* Data Freshness */}
      <section className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-3">
          <div className="flex items-center justify-center gap-2 text-sm text-slate-600">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            <span>Updated hourly from official government sources and court records.</span>
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-slate-900">DOJ</div>
              <div className="text-sm text-slate-500">Press Releases</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-900">FBI</div>
              <div className="text-sm text-slate-500">News Stories</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-900">SEC</div>
              <div className="text-sm text-slate-500">Litigation</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-900">50</div>
              <div className="text-sm text-slate-500">State AGs</div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Hero Story */}
        {heroStory && (
          <section className="mb-12">
            <div className="flex items-center gap-2 mb-4">
              <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
              <h2 className="text-sm font-semibold text-red-600 uppercase tracking-wide">
                Top Story
              </h2>
            </div>
            <div className="bg-white border-2 border-slate-200 rounded-xl p-6 hover:shadow-xl transition-shadow">
              <StoryCard story={heroStory} />
            </div>
          </section>
        )}

        {/* Two Column Layout */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Column */}
          <div className="lg:col-span-2 space-y-8">
            {/* Latest Stories */}
            <section>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-slate-900">Latest Cases</h2>
                <Link
                  href="/stories"
                  className="text-sm text-red-600 hover:text-red-700 font-medium"
                >
                  View All →
                </Link>
              </div>
              {remainingTopStories.length > 0 ? (
                <div className="space-y-4">
                  {remainingTopStories.map((story) => (
                    <StoryCard key={story.id} story={story} />
                  ))}
                </div>
              ) : (
                <div className="bg-slate-100 rounded-lg p-8 text-center">
                  <p className="text-slate-600 mb-4">
                    No stories yet. Stories will appear here once the data pipeline is running.
                  </p>
                  <p className="text-sm text-slate-500">
                    Set up n8n workflows to start ingesting from DOJ, FBI, and SEC.
                  </p>
                </div>
              )}
            </section>
          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            {/* Minnesota Watch */}
            <section className="bg-blue-50 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">🏔️</span>
                <div>
                  <h2 className="font-bold text-blue-900">Minnesota Watch</h2>
                  <p className="text-xs text-blue-700">Priority state coverage</p>
                </div>
              </div>
              {mnStories.length > 0 ? (
                <div className="space-y-2">
                  {mnStories.map((story) => (
                    <StoryCard key={story.id} story={story} compact />
                  ))}
                </div>
              ) : (
                <p className="text-sm text-blue-700">
                  No recent Minnesota stories. Check back soon.
                </p>
              )}
              <Link
                href="/states/minnesota"
                className="block mt-4 text-center text-sm text-blue-700 hover:text-blue-900 font-medium"
              >
                All Minnesota Coverage →
              </Link>
            </section>

            {/* California Watch */}
            <section className="bg-amber-50 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">🌴</span>
                <div>
                  <h2 className="font-bold text-amber-900">California Watch</h2>
                  <p className="text-xs text-amber-700">Priority state coverage</p>
                </div>
              </div>
              {caStories.length > 0 ? (
                <div className="space-y-2">
                  {caStories.map((story) => (
                    <StoryCard key={story.id} story={story} compact />
                  ))}
                </div>
              ) : (
                <p className="text-sm text-amber-700">
                  No recent California stories. Check back soon.
                </p>
              )}
              <Link
                href="/states/california"
                className="block mt-4 text-center text-sm text-amber-700 hover:text-amber-900 font-medium"
              >
                All California Coverage →
              </Link>
            </section>

            {/* Newsletter Sidebar CTA */}
            <section className="bg-slate-900 text-white rounded-xl p-5">
              <h2 className="font-bold mb-2">Stay Informed</h2>
              <p className="text-sm text-slate-300 mb-4">
                Get fraud alerts from DOJ, FBI, and SEC delivered to your inbox daily.
              </p>
              <NewsletterForm variant="inline" />
            </section>
          </div>
        </div>

        {/* Recently Added */}
        {recentStories.length > 0 && (
          <section className="mt-12 pt-8 border-t">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Just Added</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recentStories.map((story) => (
                <StoryCard key={story.id} story={story} compact />
              ))}
            </div>
          </section>
        )}
       </div>

      {/* How We Source Data */}
      <section className="bg-white border-t">
        <div className="max-w-6xl mx-auto px-4 py-12">
          <div className="text-center mb-8">
            <h2 className="text-2xl md:text-3xl font-bold text-slate-900 mb-2">
              How We Source Data
            </h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Every story is tied to an official government record. We ingest from public
              agencies, verify links, and prioritize impact.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-slate-50 rounded-xl p-6 border">
              <h3 className="font-semibold text-slate-900 mb-2">Official Sources</h3>
              <p className="text-sm text-slate-600">
                DOJ, FBI, SEC, FTC, state attorneys general, and federal court records.
              </p>
            </div>
            <div className="bg-slate-50 rounded-xl p-6 border">
              <h3 className="font-semibold text-slate-900 mb-2">Automated Ingestion</h3>
              <p className="text-sm text-slate-600">
                Hourly workflows detect new releases and tag fraud categories and states.
              </p>
            </div>
            <div className="bg-slate-50 rounded-xl p-6 border">
              <h3 className="font-semibold text-slate-900 mb-2">Source Verification</h3>
              <p className="text-sm text-slate-600">
                Every case links back to the original document so you can verify the facts.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="bg-red-600 text-white py-12">

        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Never Miss a Fraud Case
          </h2>
          <p className="text-lg text-red-100 mb-6">
            Join thousands who get daily updates on fraud, waste, and corruption from official government sources.
          </p>
          <div className="max-w-md mx-auto">
            <NewsletterForm variant="hero" />
          </div>
        </div>
      </section>
    </div>
  );
}
