import './VoiceOrb.css'

export type OrbState = 'idle' | 'recording' | 'thinking' | 'speaking'

const LABELS: Record<OrbState, string> = {
  idle:      'Tap to speak',
  recording: 'Tap to send',
  thinking:  'Thinking…',
  speaking:  'Speaking…',
}

interface Props {
  state: OrbState
  onClick: () => void
}

export default function VoiceOrb({ state, onClick }: Props) {
  const interactive = state === 'idle' || state === 'recording'

  return (
    <div className="orb-wrapper">
      <button
        className={`orb orb--${state}`}
        onClick={interactive ? onClick : undefined}
        disabled={!interactive}
        aria-label={LABELS[state]}
        aria-pressed={state === 'recording'}
      />
      <p className="orb-label">{LABELS[state]}</p>
    </div>
  )
}
