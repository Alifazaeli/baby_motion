'use client';

interface Props {
  value: boolean;
  onChange: (v: boolean) => void;
  label: string;
}

/** FR-W2: Toggle to include stories from younger age groups (matches FR-A12). */
export function YoungerStoriesToggle({ value, onChange, label }: Props) {
  return (
    <label className="flex items-center justify-between cursor-pointer py-2">
      <span className="text-sm text-gray-600">{label}</span>
      <div
        className={`relative inline-block w-11 h-6 rounded-full transition-colors ${value ? 'bg-primary' : 'bg-gray-300'}`}
        onClick={() => onChange(!value)}
      >
        <span
          className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${value ? 'translate-x-5' : ''}`}
        />
      </div>
    </label>
  );
}
