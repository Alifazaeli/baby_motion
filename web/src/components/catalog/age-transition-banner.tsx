'use client';

import { useTranslations } from 'next-intl';
import type { Child } from '@/types';

interface Props {
  child: Child;
  onDismiss: () => void;
}

/** FR-W2: Age transition banner (matches Flutter FR-A11). */
export function AgeTransitionBanner({ child, onDismiss }: Props) {
  const t = useTranslations('catalog');
  return (
    <div className="mx-4 mt-4 bg-orange-50 border border-orange-200 rounded-2xl p-4 flex items-start gap-3">
      <span className="text-2xl">🎉</span>
      <p className="flex-1 text-sm text-gray-700">
        {t('age_transition_banner', { name: child.name, months: child.ageInMonths })}
      </p>
      <button onClick={onDismiss} className="text-gray-400 hover:text-gray-600 text-lg">×</button>
    </div>
  );
}
