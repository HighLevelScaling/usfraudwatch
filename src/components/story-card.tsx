import { formatDistanceToNow } from 'date-fns';
import { ExternalLink } from 'lucide-react';
import { Story, FRAUD_TYPE_LABELS, FraudType, STATE_NAMES } from '@/types/database';
import { getSourceColor } from '@/lib/utils';

interface StoryCardProps {
  story: Story;
  compact?: boolean;
}

export function StoryCard({ story, compact = false }: StoryCardProps) {
  const sourceColor = getSourceColor(story.source_name);
  const fraudLabel = story.fraud_type
    ? FRAUD_TYPE_LABELS[story.fraud_type as FraudType] || story.fraud_type
    : null;
  const stateName = story.state ? STATE_NAMES[story.state] || story.state : null;

  const timeAgo = story.published_at
    ? formatDistanceToNow(new Date(story.published_at), { addSuffix: true })
    : 'Recently';

  if (compact) {
    return (
      <article className="border-l-4 border-slate-200 pl-4 py-3 hover:border-red-500 transition-colors group">
        <a
          href={story.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="block"
        >
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-xs px-2 py-0.5 rounded ${sourceColor}`}>
              {story.source_name}
            </span>
            {story.state && (
              <span className="text-xs text-slate-500">{story.state}</span>
            )}
          </div>
          <h3 className="font-medium text-slate-900 group-hover:text-red-600 line-clamp-2 transition-colors">
            {story.title}
          </h3>
          <p className="text-xs text-slate-500 mt-1">{timeAgo}</p>
        </a>
      </article>
    );
  }

  return (
    <article className="bg-white border border-slate-200 rounded-lg p-5 hover:shadow-lg transition-shadow group">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          {/* Metadata row */}
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <span className={`text-xs px-2 py-1 rounded font-medium ${sourceColor}`}>
              {story.source_name}
            </span>
            {fraudLabel && (
              <span className="text-xs text-slate-600">{fraudLabel}</span>
            )}
            {stateName && (
              <span className="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded">
                {stateName}
              </span>
            )}
            {story.importance_score >= 80 && (
              <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded font-medium">
                High Priority
              </span>
            )}
          </div>

          {/* Title */}
          <a
            href={story.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="block group/link"
          >
            <h3 className="text-lg font-semibold text-slate-900 group-hover/link:text-red-600 transition-colors mb-2 line-clamp-2">
              {story.title}
              <ExternalLink className="inline-block w-4 h-4 ml-2 opacity-0 group-hover/link:opacity-100 transition-opacity" />
            </h3>
          </a>

          {/* Summary */}
          {story.summary && (
            <p className="text-slate-600 text-sm line-clamp-2 mb-3">
              {story.summary}
            </p>
          )}

          {/* Entities preview */}
          {story.entities && (
            <div className="flex flex-wrap gap-2 mb-3">
              {story.entities.dollar_amounts?.slice(0, 2).map((amount, i) => (
                <span
                  key={i}
                  className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded"
                >
                  {amount}
                </span>
              ))}
              {story.entities.defendants?.slice(0, 2).map((name, i) => (
                <span
                  key={i}
                  className="text-xs bg-amber-50 text-amber-700 px-2 py-1 rounded"
                >
                  {name}
                </span>
              ))}
            </div>
          )}

          {/* Footer */}
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>{timeAgo}</span>
            <a
              href={story.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-red-600 hover:text-red-700 font-medium"
            >
              Read Full Story →
            </a>
          </div>
        </div>
      </div>
    </article>
  );
}
