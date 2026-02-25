import { Metadata } from 'next';
import { supabase } from '@/lib/supabase';
import { Story } from '@/types/database';
import { StoryCard } from '@/components/story-card';
import { NewsletterForm } from '@/components/newsletter-form';

export const metadata: Metadata = {
  title: 'Minnesota Fraud Watch',
  description:
    'Tracking fraud, waste, and corruption in Minnesota. DOJ, FBI, Minnesota AG cases.',
};

export const revalidate = 3600;

async function getMinnesotaStories(): Promise<Story[]> {
  const { data, error } = await supabase
    .from('stories')
    .select('*')
    .eq('state', 'MN')
    .order('published_at', { ascending: false })
    .limit(50);

  if (error) {
    console.error('Error fetching Minnesota stories:', error);
    return [];
  }

  return data || [];
}

export default async function MinnesotaPage() {
  const stories = await getMinnesotaStories();

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="bg-gradient-to-b from-blue-900 to-blue-800 text-white py-12">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex items-center gap-4 mb-4">
            <span className="text-5xl">🏔️</span>
            <div>
              <h1 className="text-4xl font-bold">Minnesota Fraud Watch</h1>
              <p className="text-blue-200">Priority state coverage</p>
            </div>
          </div>
          <p className="text-xl text-blue-100 max-w-2xl">
            Tracking fraud, waste, and corruption cases in Minnesota from the DOJ,
            FBI, Minnesota Attorney General, and federal courts.
          </p>
        </div>
      </section>

      {/* Sources */}
      <section className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h2 className="text-sm font-semibold text-slate-500 mb-2">
            Minnesota Sources
          </h2>
          <div className="flex flex-wrap gap-4 text-sm">
            <a
              href="https://www.ag.state.mn.us/Office/Communications.asp"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              MN Attorney General →
            </a>
            <a
              href="https://www.auditor.leg.state.mn.us/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              MN Legislative Auditor →
            </a>
            <a
              href="https://mncourts.gov/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              MN Courts →
            </a>
            <a
              href="https://www.justice.gov/usao-mn"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              US Attorney - MN →
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
                ? `${stories.length} Minnesota Cases`
                : 'Minnesota Cases'}
            </h2>

            {stories.length > 0 ? (
              <div className="space-y-4">
                {stories.map((story) => (
                  <StoryCard key={story.id} story={story} />
                ))}
              </div>
            ) : (
              <div className="bg-blue-50 rounded-lg p-8 text-center">
                <p className="text-blue-800 mb-4">
                  No Minnesota stories yet. Stories will appear here once the data
                  pipeline is running.
                </p>
                <p className="text-sm text-blue-600">
                  We monitor the Minnesota AG, US Attorney for Minnesota, and
                  federal cases mentioning Minnesota.
                </p>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Newsletter */}
            <section className="bg-blue-900 text-white rounded-xl p-5">
              <h2 className="font-bold mb-2">Minnesota Alerts</h2>
              <p className="text-sm text-blue-200 mb-4">
                Get Minnesota fraud cases delivered to your inbox.
              </p>
              <NewsletterForm variant="inline" states={['MN']} />
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
                  <dd className="font-semibold">4+</dd>
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
                specifically mentioning Minnesota from federal and state sources.
                All links go directly to official government documents.
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
