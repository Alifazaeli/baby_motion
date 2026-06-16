import Link from 'next/link';
import Image from 'next/image';
import type { Category, Story } from '@/types';

interface Props {
  category: Category;
  stories: Story[];
  locale: string;
}

/** Horizontal scrolling row of story cards within a category (FR-W2). */
export function CategoryRow({ category, stories, locale }: Props) {
  return (
    <section className="mt-8">
      <h2 className="px-6 text-lg font-bold mb-3">{category.name}</h2>
      <div className="flex gap-4 overflow-x-auto ps-6 pe-6 pb-2 scrollbar-hide">
        {stories.map((story) => (
          <Link
            key={story.id}
            href={`/${locale}/story/${story.id}`}
            className="flex-shrink-0 w-36"
          >
            <div className="relative w-36 h-36 rounded-2xl overflow-hidden bg-gray-100">
              {story.coverUrl && (
                <Image src={story.coverUrl} alt={story.title} fill className="object-cover" />
              )}
            </div>
            <p className="mt-2 text-sm font-semibold line-clamp-2">{story.title}</p>
            <p className="text-xs text-gray-400">{Math.ceil(story.durationSeconds / 60)} min</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
