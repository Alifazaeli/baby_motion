'use client';

import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { useParams } from 'next/navigation';
import { GoogleLogin } from '@react-oauth/google';
import { signInWithGoogle } from '@/lib/auth/auth-service';
import { api } from '@/lib/api/endpoints';

export default function LoginPage() {
  const t = useTranslations('auth');
  const router = useRouter();
  const { locale } = useParams<{ locale: string }>();

  const handleSuccess = async (credentialResponse: { credential?: string }) => {
    if (!credentialResponse.credential) return;
    try {
      await signInWithGoogle(credentialResponse.credential);
      const me = await api.users.getMe();
      const destination = me.children.length === 0 ? 'onboarding' : 'catalog';
      router.push(`/${locale}/${destination}`);
    } catch (err) {
      console.error('Sign-in failed:', err);
    }
  };

  return (
    <main className="min-h-screen bg-surface flex flex-col items-center justify-center px-6">
      <h1 className="text-4xl font-extrabold text-primary mb-2">{t('title')}</h1>
      <p className="text-gray-500 mb-10">BabyMotion</p>
      <GoogleLogin onSuccess={handleSuccess} shape="pill" size="large" />
    </main>
  );
}
