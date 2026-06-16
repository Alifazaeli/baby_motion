/**
 * Marketing landing page — fully SSR (FR-W1, FR-W4).
 */
import { getTranslations, setRequestLocale } from 'next-intl/server';
import type { Metadata } from 'next';
import Link from 'next/link';

interface Props {
  params: Promise<{ locale: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations({ locale, namespace: 'landing' });
  return {
    title: t('hero_title'),
    description: t('hero_subtitle'),
    alternates: {
      languages: { fa: '/fa', en: '/en' },
    },
    other: {
      'hreflang:fa': '/fa',
      'hreflang:en': '/en',
    },
  };
}

export default async function LandingPage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations({ locale, namespace: 'landing' });

  return (
    <main className="min-h-screen bg-surface">
      {/* Hero */}
      <section className="flex flex-col items-center justify-center min-h-screen px-6 text-center">
        <h1 className="text-6xl font-extrabold text-primary mb-4">{t('hero_title')}</h1>
        <p className="text-xl text-gray-600 mb-10 max-w-md">{t('hero_subtitle')}</p>
        <Link
          href={`/${locale}/login`}
          className="bg-primary text-white font-bold text-lg px-8 py-4 rounded-2xl hover:opacity-90 transition-opacity"
        >
          {t('cta')}
        </Link>

        {/* Feature highlights */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl">
          {(['feature_age', 'feature_languages', 'feature_no_ads'] as const).map((key) => (
            <div key={key} className="bg-white rounded-2xl p-6 shadow-sm text-start">
              <p className="text-gray-700">{t(key)}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
