import { Metadata } from 'next';
import { supabase } from '@/lib/supabase';
import { Story } from '@/types/database';
import { StoryCard } from '@/components/story-card';
import { NewsletterForm } from '@/components/newsletter-form';

export const metadata: Metadata = {
  title: 'California Fraud Watch',
  description:
    'Tracking fraud, waste, and corruption in California. DOJ, FBI, California AG cases.',
};

export const revalidate = 3600;

async function getCaliforniaStories(): Promise<Story[]> {
  const { data, error } = await supabase
    .from('stories')
    .select('*')
    .eq('state', 'CA')
    .order('published_at', { ascending: false })
    .limit(50);

  if (error) {
    console.error('Error fetching California stories:', error);
    return [];
  }

  return data || [];
}

export default async function CaliforniaPage() {
  const stories = await getCaliforniaStories();

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="bg-gradient-to-b from-amber-700 to-amber-600 text-white py-12">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex items-center gap-4 mb-4">
            <span className="text-5xl">🌴</span>
            <div>
              <h1 className="text-4xl font-bold">California Fraud Watch</h1>
              <p className="text-amber-200">Priority state coverage</p>
            </div>
          </div>
          <p className="text-xl text-amber-100 max-w-2xl">
            Tracking fraud, waste, and corruption cases in California from the DOJ,
            FBI, California Attorney General, State Auditor, and federal courts.
          </p>
        </div>
      </section>

      {/* Sources */}
      <section className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h2 className="text-sm font-semibold text-slate-500 mb-2">
            California Sources
          </h2>
          <div className="flex flex-wrap gap-4 text-sm">
            <a
              href="https://oag.ca.gov/news"
              target="_blank"
              rel="noopener noreferrer"
              className="text-amber-700 hover:underline"
            >
              CA Attorney General →
            </a>
            <a
              href="https://www.auditor.ca.gov/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-amber-700 hover:underline"
            >
              CA State Auditor →
            </a>
            <a
              href="https://www.courts.ca.gov/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-amber-700 hover:underline"
            >
              CA Courts →
            </a>
            <a
              href="https://www.justice.gov/usao-cdca"
              target="_blank"
              rel="noopener noreferrer"
              className="text-amber-700 hover:underline"
            >
              US Attorney - Central CA →
            </a>
            <a
              href="https://www.justice.gov/usao-ndca"
              target="_blank"
              rel="noopener noreferrer"
              className="text-amber-700 hover:underline"
            >
              US Attorney - Northern CA →
            </a>
          </div>
        </div>
      </section>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <h2 className="text-xl font-bold text-slate-900 mb-4">
              {stories.length > 0
                ? `${stories.length} California Cases`
                : 'California Cases'}
            </h2>

            {stories.length > 0 ? (
              <div className="space-y-4">
                {stories.map((story) => (
                  <StoryCard key={story.id} story={story} />
                ))}
              </div>
            ) : (
              <div className="bg-amber-50 rounded-lg p-8 text-center">
                <p className="text-amber-800 mb-4">
                  No California stories yet. Stories will appear here once the data
                  pipeline is running.
                </p>
                <p className="text-sm text-amber-600">
                  We monitor the California AG, CA State Auditor, US Attorneys for
                  California, and federal cases mentioning California.
                </p>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Newsletter */}
            <section className="bg-amber-700 text-white rounded-xl p-5">
              <h2 className="font-bold mb-2">California Alerts</h2>
              <p className="text-sm text-amber-200 mb-4">
                Get California fraud cases delivered to your inbox.
              </p>
              <NewsletterForm variant="inline" states={['CA']} />
            </section>

            {/* Stats */}
            <section className="bg-slate-100 rounded-xl p-5">
              <h2 className="font-bold text-slate-900 mb-4">Coverage</h2>
              <dl className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <dt className="text-slate-600">Stories Tracked</dt>
                  <dd className="font-semibold">{stories.length}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-600">Sources Monitored</dt>
                  <dd className="font-semibold">6+</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-600">Update Frequency</dt>
                  <dd className="font-semibold">Hourly</dd>
                </div>
              </dl>
            </section>

            {/* About */}
            <section className="bg-white border rounded-xl p-5">
              <h2 className="font-bold text-slate-900 mb-2">About This Page</h2>
              <p className="text-sm text-slate-600">
                We aggregate fraud-related press releases and court filings
                specifically mentioning California from federal and state sources.
                All links go directly to official government documents.
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
