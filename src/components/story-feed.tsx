import { Story } from '@/types/database';
import { StoryCard } from './story-card';

interface StoryFeedProps {
  stories: Story[];
  title?: string;
  compact?: boolean;
  showEmpty?: boolean;
  emptyMessage?: string;
}

export function StoryFeed({
  stories,
  title,
  compact = false,
  showEmpty = true,
  emptyMessage = 'No stories found.',
}: StoryFeedProps) {
  if (stories.length === 0 && !showEmpty) {
    return null;
  }

  return (
    <section>
      {title && (
        <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
          {title}
        </h2>
      )}

      {stories.length === 0 ? (
        <div className="bg-slate-100 rounded-lg p-8 text-center text-slate-500">
          {emptyMessage}
        </div>
      ) : (
        <div className={compact ? 'space-y-2' : 'space-y-4'}>
          {stories.map((story) => (
            <StoryCard key={story.id} story={story} compact={compact} />
          ))}
        </div>
      )}
    </section>
  );
}
