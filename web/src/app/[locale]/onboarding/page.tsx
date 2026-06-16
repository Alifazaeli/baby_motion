'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter, useParams } from 'next/navigation';
import { api } from '@/lib/api/endpoints';

const AGE_GROUP_LABELS: Record<string, string> = {
  '12_18m': '12–18 months',
  '18_30m': '18–30 months',
  '30_42m': '30–42 months',
  '42_60m': '42–60 months',
  '60m_plus': '60+ months',
};

function computeAgeGroup(year: number, month: number): string | null {
  const now = new Date();
  const months = (now.getFullYear() - year) * 12 + (now.getMonth() + 1 - month);
  if (months < 12) return null;
  if (months < 18) return '12_18m';
  if (months < 30) return '18_30m';
  if (months < 42) return '30_42m';
  if (months < 60) return '42_60m';
  return '60m_plus';
}

export default function OnboardingPage() {
  const t = useTranslations('onboarding');
  const router = useRouter();
  const { locale } = useParams<{ locale: string }>();

  const [step, setStep] = useState(0);
  const [name, setName] = useState('');
  const [birthYear, setBirthYear] = useState(new Date().getFullYear() - 2);
  const [birthMonth, setBirthMonth] = useState(1);
  const [language, setLanguage] = useState(locale === 'fa' ? 'fa' : 'en');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 7 }, (_, i) => currentYear - 6 + i);
  const months = Array.from({ length: 12 }, (_, i) => i + 1);
  const ageGroup = computeAgeGroup(birthYear, birthMonth);

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    try {
      await api.users.createChild({ name, birthYear, birthMonth, language });
      router.push(`/${locale}/catalog`);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-surface flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-md">
        <p className="text-sm text-gray-400 mb-4 text-center">{step + 1} / 3</p>

        {step === 0 && (
          <div className="space-y-6">
            <h1 className="text-2xl font-bold">{t('step1_title')}</h1>
            <input
              className="w-full border-2 border-gray-200 rounded-xl px-4 py-3 text-lg"
              placeholder={t('child_name_hint')}
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
            <button
              className="w-full bg-primary text-white font-bold py-3 rounded-2xl disabled:opacity-50"
              disabled={!name.trim()}
              onClick={() => setStep(1)}
            >
              {t('continue')}
            </button>
          </div>
        )}

        {step === 1 && (
          <div className="space-y-6">
            <h1 className="text-2xl font-bold">{t('step2_title', { name })}</h1>
            <div className="flex gap-4">
              <select
                className="flex-1 border-2 border-gray-200 rounded-xl px-4 py-3"
                value={birthYear}
                onChange={(e) => setBirthYear(Number(e.target.value))}
              >
                {years.map((y) => <option key={y} value={y}>{y}</option>)}
              </select>
              <select
                className="flex-1 border-2 border-gray-200 rounded-xl px-4 py-3"
                value={birthMonth}
                onChange={(e) => setBirthMonth(Number(e.target.value))}
              >
                {months.map((m) => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>
            {ageGroup && (
              <div className="bg-orange-50 rounded-2xl p-4 text-primary font-semibold">
                {t('age_group_preview', { group: AGE_GROUP_LABELS[ageGroup] ?? ageGroup })}
              </div>
            )}
            <button className="w-full bg-primary text-white font-bold py-3 rounded-2xl" onClick={() => setStep(2)}>
              {t('continue')}
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6">
            <h1 className="text-2xl font-bold">{t('step3_title')}</h1>
            {([['fa', t('language_persian')], ['en', t('language_english')]] as [string, string][]).map(([code, label]) => (
              <button
                key={code}
                className={`w-full border-2 rounded-2xl py-4 text-lg font-semibold transition-colors ${
                  language === code ? 'border-primary text-primary bg-orange-50' : 'border-gray-200'
                }`}
                onClick={() => setLanguage(code)}
              >
                {label}
              </button>
            ))}
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <button
              className="w-full bg-primary text-white font-bold py-3 rounded-2xl disabled:opacity-50"
              disabled={loading}
              onClick={handleSubmit}
            >
              {loading ? '…' : t('get_started')}
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
