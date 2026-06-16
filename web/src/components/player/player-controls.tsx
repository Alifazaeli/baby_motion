'use client';

import { useTranslations } from 'next-intl';

interface Props {
  isPlaying: boolean;
  onPlayPause: () => void;
  onPrevious: () => void;
  onNext: () => void;
  onReplay: () => void;
  onExit: () => void;
}

/** FR-W3: Responsive player controls. */
export function PlayerControls({ isPlaying, onPlayPause, onPrevious, onNext, onReplay, onExit }: Props) {
  const t = useTranslations('player');

  return (
    <div className="flex items-center justify-around py-3">
      <CtrlBtn onClick={onExit} label={t('exit')}>✕</CtrlBtn>
      <CtrlBtn onClick={onPrevious} label={t('previous')}>⏮</CtrlBtn>
      <button
        onClick={onPlayPause}
        aria-label={isPlaying ? t('pause') : t('play')}
        className="w-16 h-16 bg-white rounded-full text-3xl flex items-center justify-center shadow-lg"
      >
        {isPlaying ? '⏸' : '▶'}
      </button>
      <CtrlBtn onClick={onNext} label={t('next')}>⏭</CtrlBtn>
      <CtrlBtn onClick={onReplay} label={t('replay')}>↺</CtrlBtn>
    </div>
  );
}

function CtrlBtn({ onClick, label, children }: { onClick: () => void; label: string; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      aria-label={label}
      className="w-11 h-11 bg-white/20 rounded-full text-white text-xl flex items-center justify-center"
    >
      {children}
    </button>
  );
}
