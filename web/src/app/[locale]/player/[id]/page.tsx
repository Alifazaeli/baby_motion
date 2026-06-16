'use client';

import { useEffect, useRef, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
import { api } from '@/lib/api/endpoints';
import { PlayerControls } from '@/components/player/player-controls';
import type { Manifest, Scene } from '@/types';

export default function PlayerPage() {
  const { id, locale } = useParams<{ id: string; locale: string }>();
  const router = useRouter();
  const t = useTranslations('player');

  const audioRef = useRef<HTMLAudioElement>(null);
  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [sceneIndex, setSceneIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [scenesWatched, setScenesWatched] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const me = await api.users.getMe();
      const child = me.children[0];
      if (!child) return;

      const story = await api.content.getStory(id, child.language);
      const manifestRes = await fetch(story.manifestUrl);
      const manifestData: Manifest = await manifestRes.json();
      setManifest(manifestData);

      const session = await api.analytics.startStory(id, child.id, child.language);
      setSessionId(session.sessionId);
      setLoading(false);
    })();
  }, [id]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !manifest) return;
    const handler = () => {
      const scene = manifest.scenes[sceneIndex];
      if (audio.currentTime >= scene.audioEndSec && sceneIndex < manifest.scenes.length - 1) {
        const next = sceneIndex + 1;
        setSceneIndex(next);
        setScenesWatched(next + 1);
      }
    };
    audio.addEventListener('timeupdate', handler);
    return () => audio.removeEventListener('timeupdate', handler);
  }, [manifest, sceneIndex]);

  const currentScene: Scene | undefined = manifest?.scenes[sceneIndex];
  const isComplete = manifest ? sceneIndex >= manifest.scenes.length - 1 && !isPlaying : false;

  const handleExit = async () => {
    if (sessionId) {
      isComplete
        ? await api.analytics.completeSession(sessionId, scenesWatched)
        : await api.analytics.abandonSession(sessionId, scenesWatched);
    }
    router.push(`/${locale}/catalog`);
  };

  const seekToScene = (index: number) => {
    if (!manifest || !audioRef.current) return;
    const scene = manifest.scenes[index];
    audioRef.current.currentTime = scene.audioStartSec;
    setSceneIndex(index);
  };

  if (loading) return <div className="min-h-screen bg-black flex items-center justify-center text-white">{t('loading')}</div>;

  return (
    <main className="min-h-screen bg-black relative overflow-hidden">
      {currentScene && (
        <div className="absolute inset-0">
          <Image src={currentScene.imageUrl} alt={currentScene.text} fill className="object-cover" priority />
          <div className="absolute bottom-24 left-4 right-4 bg-black/60 rounded-2xl p-4 text-white text-center text-xl leading-relaxed">
            {currentScene.text}
          </div>
        </div>
      )}

      {manifest && (
        <audio
          ref={audioRef}
          src={manifest.audioUrl}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          autoPlay
        />
      )}

      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
        <PlayerControls
          isPlaying={isPlaying}
          onPlayPause={() => isPlaying ? audioRef.current?.pause() : audioRef.current?.play()}
          onPrevious={() => sceneIndex > 0 && seekToScene(sceneIndex - 1)}
          onNext={() => manifest && sceneIndex < manifest.scenes.length - 1 && seekToScene(sceneIndex + 1)}
          onReplay={() => { setSceneIndex(0); if (audioRef.current) { audioRef.current.currentTime = 0; audioRef.current.play(); } }}
          onExit={handleExit}
        />
      </div>
    </main>
  );
}
