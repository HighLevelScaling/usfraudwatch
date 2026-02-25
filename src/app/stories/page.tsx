import { Metadata } from 'next';
import { supabase } from '@/lib/supabase';
import { Story, FRAUD_TYPE_LABELS, FraudType, STATE_NAMES } from '@/types/database';
import { StoryCard } from '@/components/story-card';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'All Fraud Stories',
  description:
    'Browse all fraud, waste, and corruption stories from DOJ, FBI, SEC, and state attorneys general.',
};

export const revalidate = 1800; // 30 minutes

interface PageProps {
  searchParams: Promise<{
    type?: string;
    source?: string;
    state?: string;
    page?: string;
  }>;
}

async function getStories(filters: {
  type?: string;
  source?: string;
  state?: string;
  limit: number;
}): Promise<{ stories: Story[]; total: number }> {
  let query = supabase
    .from('stories')
    .select('*', { count: 'exact' })
    .order('published_at', { ascending: false })
    .limit(filters.limit);

  if (filters.type) {
    query = query.eq('fraud_type', filters.type);
  }
  if (filters.source) {
    query = query.ilike('source_name', `%${filters.source}%`);
  }
  if (filters.state) {
    query = query.eq('state', filters.state);
  }

  const { data, error, count } = await query;

  if (error) {
    console.error('Error fetching stories:', error);
    return { stories: [], total: 0 };
  }

  return { stories: data || [], total: count || 0 };
}

export default async function StoriesPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const page = Math.max(1, Number.parseInt(params.page ?? '1', 10) || 1);
  const pageSize = 20;
  const limit = page * pageSize;

  const { stories, total } = await getStories({
    type: params.type,
    source: params.source,
    state: params.state,
    limit,
  });

  const hasMore = stories.length < total;

  const fraudTypes = Object.entries(FRAUD_TYPE_LABELS) as [FraudType, string][];
  const sources = ['DOJ', 'FBI', 'SEC', 'FTC', 'HHS'];
  const states = [
    { code: 'MN', name: 'Minnesota' },
    { code: 'CA', name: 'California' },
    { code: 'TX', name: 'Texas' },
    { code: 'NY', name: 'New York' },
    { code: 'FL', name: 'Florida' },
  ];

  const activeFilters = [
    params.type
      ? {
          key: 'type' as const,
          label: FRAUD_TYPE_LABELS[params.type as FraudType] || params.type,
        }
      : null,
    params.source ? { key: 'source' as const, label: params.source } : null,
    params.state
      ? {
          key: 'state' as const,
          label: STATE_NAMES[params.state] || params.state,
        }
      : null,
  ].filter(Boolean) as Array<{ key: 'type' | 'source' | 'state'; label: string }>;

  const createHref = (nextParams: {
    type?: string;
    source?: string;
    state?: string;
    page?: string;
  }) => {
    const search = new URLSearchParams();
    if (nextParams.type) search.set('type', nextParams.type);
    if (nextParams.source) search.set('source', nextParams.source);
    if (nextParams.state) search.set('state', nextParams.state);
    if (nextParams.page && nextParams.page !== '1') {
      search.set('page', nextParams.page);
    }
    const query = search.toString();
    return query ? `/stories?${query}` : '/stories';
  };

  const filterLinks = {
    type: createHref({ source: params.source, state: params.state }),
    source: createHref({ type: params.type, state: params.state }),
    state: createHref({ type: params.type, source: params.source }),
  };

  const nextPageHref = createHref({
    type: params.type,
    source: params.source,
    state: params.state,
    page: String(page + 1),
  });

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <section className="bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            All Fraud Stories
          </h1>
          <p className="text-slate-600">
            Browse fraud cases from DOJ, FBI, SEC, and state attorneys general.
          </p>
        </div>
      </section>

      {/* Filters */}
      <section className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-3">
          <div className="flex flex-wrap gap-4">
            {/* Type Filter */}
            <div>
              <label className="text-xs text-slate-500 block mb-1">
                Fraud Type
              </label>
              <div className="flex flex-wrap gap-1">
                <Link
                  href="/stories"
                  className={`text-xs px-2 py-1 rounded ${
                    !params.type
                      ? 'bg-red-600 text-white'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  All
                </Link>
                {fraudTypes.slice(0, 5).map(([key, label]) => (
                  <Link
                    key={key}
                    href={`/stories?type=${key}`}
                    className={`text-xs px-2 py-1 rounded ${
                      params.type === key
                        ? 'bg-red-600 text-white'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    {label.split(' ')[0]}
                  </Link>
                ))}
              </div>
            </div>

            {/* Source Filter */}
            <div>
              <label className="text-xs text-slate-500 block mb-1">Source</label>
              <div className="flex flex-wrap gap-1">
                <Link
                  href="/stories"
                  className={`text-xs px-2 py-1 rounded ${
                    !params.source
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  All
                </Link>
                {sources.map((source) => (
                  <Link
                    key={source}
                    href={`/stories?source=${source}`}
                    className={`text-xs px-2 py-1 rounded ${
                      params.source === source
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    {source}
                  </Link>
                ))}
              </div>
            </div>

            {/* State Filter */}
            <div>
              <label className="text-xs text-slate-500 block mb-1">State</label>
              <div className="flex flex-wrap gap-1">
                <Link
                  href="/stories"
                  className={`text-xs px-2 py-1 rounded ${
                    !params.state
                      ? 'bg-green-600 text-white'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  All
                </Link>
                {states.map((state) => (
                  <Link
                    key={state.code}
                    href={`/stories?state=${state.code}`}
                    className={`text-xs px-2 py-1 rounded ${
                      params.state === state.code
                        ? 'bg-green-600 text-white'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    {state.code}
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stories */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <p className="text-slate-600">
            Showing {stories.length} of {total} {total === 1 ? 'story' : 'stories'}
          </p>
        </div>

        {activeFilters.length > 0 && (
          <div className="mb-6 flex flex-wrap items-center gap-2">
            <span className="text-xs uppercase tracking-wide text-slate-500">
              Active Filters
            </span>
            {activeFilters.map((filter) => (
              <Link
                key={filter.key}
                href={filterLinks[filter.key]}
                className="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded-full hover:bg-slate-200"
              >
                {filter.label} ✕
              </Link>
            ))}
            <Link
              href="/stories"
              className="text-xs text-slate-500 hover:text-slate-700"
            >
              Clear all
            </Link>
          </div>
        )}

        {stories.length > 0 ? (
          <div>
            <div className="space-y-4">
              {stories.map((story) => (
                <StoryCard key={story.id} story={story} />
              ))}
            </div>
            {hasMore && (
              <div className="mt-8 text-center">
                <Link
                  href={nextPageHref}
                  className="inline-flex items-center justify-center px-6 py-2 rounded-lg bg-slate-900 text-white font-medium hover:bg-slate-800"
                >
                  Load more
                </Link>
                <p className="text-xs text-slate-500 mt-2">
                  Viewing {stories.length} of {total} stories.
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-lg p-8 text-center">
            <p className="text-slate-600 mb-4">
              No stories found matching your filters.
            </p>
            <Link
              href="/stories"
              className="text-red-600 hover:text-red-700 font-medium"
            >
              Clear filters →
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
