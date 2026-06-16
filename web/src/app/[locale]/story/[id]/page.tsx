'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import { api } from '@/lib/api/endpoints';
import type { Story } from '@/types';

export default function StoryDetailPage() {
  const { id, locale } = useParams<{ id: string; locale: string }>();
  const router = useRouter();
  const [story, setStory] = useState<Story | null>(null);

  useEffect(() => {
    api.users.getMe().then((me) => {
      const lang = me.children[0]?.language ?? locale;
      return api.content.getStory(id, lang);
    }).then(setStory);
  }, [id, locale]);

  if (!story) return <div className="min-h-screen bg-surface flex items-center justify-center"><div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full" /></div>;

  const minutes = Math.ceil(story.durationSeconds / 60);

  return (
    <main className="min-h-screen bg-surface">
      <button onClick={() => router.back()} className="absolute top-4 start-4 z-10 bg-white/80 rounded-full p-2">←</button>

      <div className="relative w-full h-72">
        {story.coverUrl && (
          <Image src={story.coverUrl} alt={story.title} fill className="object-cover" />
        )}
      </div>

      <div className="px-6 py-6 space-y-4">
        <h1 className="text-3xl font-extrabold">{story.title}</h1>
        <p className="text-gray-400 text-sm">{minutes} min</p>
        {story.description && <p className="text-gray-600">{story.description}</p>}

        <button
          onClick={() => router.push(`/${locale}/player/${story.id}`)}
          className="w-full bg-primary text-white font-bold text-lg py-4 rounded-2xl mt-4"
        >
          ▶ Play
        </button>
      </div>
    </main>
  );
}
