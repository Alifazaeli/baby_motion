import { getRequestConfig } from 'next-intl/server';

export const locales = ['fa', 'en'] as const;
export const defaultLocale = 'fa' as const;

export const rtlLocales: string[] = ['fa'];

export function isRtl(locale: string): boolean {
  return rtlLocales.includes(locale);
}

export default getRequestConfig(async ({ requestLocale }) => {
  const locale = (await requestLocale) ?? defaultLocale;
  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default,
  };
});
