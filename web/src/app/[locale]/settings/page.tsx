'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api/endpoints';
import { clearTokens } from '@/lib/auth/auth-service';
import type { Child } from '@/types';

export default function SettingsPage() {
  const t = useTranslations('settings');
  const { locale } = useParams<{ locale: string }>();
  const router = useRouter();
  const [child, setChild] = useState<Child | null>(null);

  useEffect(() => {
    api.users.getMe().then((me) => setChild(me.children[0] ?? null));
  }, []);

  const handleSignOut = () => {
    clearTokens();
    router.push(`/${locale}/login`);
  };

  return (
    <main className="min-h-screen bg-surface">
      <header className="px-6 py-4 border-b border-gray-100">
        <button onClick={() => router.back()} className="text-gray-500 mb-2">← Back</button>
        <h1 className="text-2xl font-extrabold">{t('title')}</h1>
      </header>

      <div className="px-6 py-6 space-y-6">
        {child && (
          <section>
            <h2 className="text-sm font-bold text-primary uppercase tracking-wide mb-3">{t('child_profile')}</h2>
            <div className="bg-white rounded-2xl divide-y divide-gray-100">
              <SettingRow label="Name" value={child.name} />
              <SettingRow label="Age" value={`${child.ageInMonths} months (${child.ageGroup ?? 'N/A'})`} />
              <SettingRow label={t('content_language')} value={child.language === 'fa' ? 'Persian' : 'English'} />
            </div>
          </section>
        )}

        <section>
          <h2 className="text-sm font-bold text-primary uppercase tracking-wide mb-3">{t('ui_language')}</h2>
          <div className="bg-white rounded-2xl divide-y divide-gray-100">
            {[['fa', 'فارسی'], ['en', 'English']].map(([code, label]) => (
              <button
                key={code}
                onClick={() => router.push(router.toString().replace(`/${locale}/`, `/${code}/`))}
                className="w-full px-4 py-3 text-start flex items-center justify-between"
              >
                <span>{label}</span>
                {locale === code && <span className="text-primary">✓</span>}
              </button>
            ))}
          </div>
        </section>

        <button
          onClick={handleSignOut}
          className="w-full py-3 text-red-500 font-semibold border-2 border-red-100 rounded-2xl hover:bg-red-50 transition-colors"
        >
          {t('sign_out')}
        </button>
      </div>
    </main>
  );
}

function SettingRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="px-4 py-3 flex items-center justify-between">
      <span className="text-gray-500">{label}</span>
      <span className="font-semibold">{value}</span>
    </div>
  );
}
