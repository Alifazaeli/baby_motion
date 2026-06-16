'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api/endpoints';
import type { Category, Child, Story } from '@/types';
import { AgeTransitionBanner } from '@/components/catalog/age-transition-banner';
import { CategoryRow } from '@/components/catalog/category-row';
import { YoungerStoriesToggle } from '@/components/catalog/younger-stories-toggle';

export default function CatalogPage() {
  const t = useTranslations('catalog');
  const { locale } = useParams<{ locale: string }>();
  const router = useRouter();

  const [child, setChild] = useState<Child | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [storiesByCategory, setStoriesByCategory] = useState<Record<string, Story[]>>({});
  const [includeYounger, setIncludeYounger] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.users.getMe().then((me) => {
      if (me.children.length === 0) { router.push(`/${locale}/onboarding`); return; }
      setChild(me.children[0]);
    });
  }, [locale, router]);

  useEffect(() => {
    if (!child) return;
    setLoading(true);
    Promise.all([
      api.content.getCategories(locale),                                              // UI locale → category names in English/Persian per URL
      api.content.getStories({ childId: child.id, language: child.language, includeYounger }), // child's content language for story translations
    ]).then(([cats, stories]) => {
      setCategories(cats);
      const grouped: Record<string, Story[]> = {};
      for (const cat of cats) grouped[cat.id] = [];
      for (const story of stories) {
        if (grouped[story.categoryId]) grouped[story.categoryId].push(story);
      }
      setStoriesByCategory(grouped);
    }).finally(() => setLoading(false));
  }, [child, includeYounger]);

  if (loading) return <main className="min-h-screen bg-surface flex items-center justify-center"><div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full" /></main>;

  return (
    <main className="min-h-screen bg-surface pb-16">
      <header className="sticky top-0 bg-surface/80 backdrop-blur-sm px-6 py-4 flex items-center justify-between border-b border-gray-100">
        <h1 className="text-2xl font-extrabold text-primary">{t('title')}</h1>
        <button onClick={() => router.push(`/${locale}/settings`)} className="text-gray-500">⚙️</button>
      </header>

      {child?.hasPendingAgeGroupTransition && (
        <AgeTransitionBanner child={child} onDismiss={() => {
          api.users.acknowledgeAgeGroup(child.id);
          setChild({ ...child, hasPendingAgeGroupTransition: false });
        }} />
      )}

      <div className="px-6 pt-4">
        <YoungerStoriesToggle value={includeYounger} onChange={setIncludeYounger} label={t('show_younger_toggle')} />
      </div>

      {categories.map((cat) => {
        const stories = storiesByCategory[cat.id] ?? [];
        if (stories.length === 0) return null;
        return (
          <CategoryRow
            key={cat.id}
            category={cat}
            stories={stories}
            locale={locale}
          />
        );
      })}
    </main>
  );
}
