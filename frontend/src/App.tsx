import { useRef, useState } from 'react'
import { Toaster, toast } from 'react-hot-toast'
import { sendVoiceMessage } from './api/chat'
import VoiceOrb, { type OrbState } from './components/VoiceOrb'
import { useVoiceRecorder } from './hooks/useVoiceRecorder'
import './App.css'

interface Turn {
  role: 'user' | 'hume'
  text: string
}

export default function App() {
  const [orbState, setOrbState] = useState<OrbState>('idle')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [turns, setTurns] = useState<Turn[]>([])

  const audioRef = useRef<HTMLAudioElement>(null)
  const audioUrlRef = useRef<string | null>(null)
  const recorder = useVoiceRecorder()

  const handleOrbClick = async () => {
    // ── Start recording ──────────────────────────────────────────────────
    if (orbState === 'idle') {
      try {
        await recorder.start()
        setOrbState('recording')
      } catch {
        // NotAllowedError — user denied mic
        toast.error('Microphone access denied. Allow it in your browser settings.')
      }
      return
    }

    // ── Stop recording → process ─────────────────────────────────────────
    if (orbState === 'recording') {
      setOrbState('thinking')
      const blob = await recorder.stop()

      try {
        const result = await sendVoiceMessage(blob, sessionId)

        setSessionId(result.sessionId)

        // Show the transcript + reply in the conversation log
        setTurns((prev) => [
          ...prev,
          { role: 'user', text: result.transcript },
          { role: 'hume', text: result.reply },
        ])

        // Revoke previous audio URL to free memory
        if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current)
        const url = URL.createObjectURL(result.audioBlob)
        audioUrlRef.current = url

        if (audioRef.current) {
          audioRef.current.src = url
          setOrbState('speaking')
          audioRef.current.play().catch(() => {
            // Autoplay blocked — still show speaking state briefly
            toast('Tap the orb to play the audio response.', { icon: '🔊' })
          })
        }
      } catch (err) {
        setOrbState('idle')
        const message = err instanceof Error ? err.message : 'Something went wrong'
        toast.error(message)
      }
    }
  }

  const handleAudioEnd = () => {
    setOrbState('idle')
  }

  return (
    <div className="app">
      <Toaster
        position="top-center"
        toastOptions={{
          style: {
            background: '#FFFFFF',
            color: '#1A1A1A',
            border: '1px solid #DDD8CE',
            fontFamily: '-apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif',
            fontSize: '0.85rem',
            boxShadow: '0 4px 16px rgba(0,0,0,0.10)',
          },
        }}
      />

      <header className="app-header">
        <h1 className="app-title">Ask Hume</h1>
        <p className="app-subtitle">David Hume's philosophy. Paddy Pimblett's mouth.</p>
      </header>

      <main className="app-main">
        <VoiceOrb state={orbState} onClick={handleOrbClick} />

        {turns.length > 0 && (
          <section className="transcript" aria-label="Conversation">
            {turns.map((turn, i) => (
              <div key={i} className={`turn turn--${turn.role}`}>
                <span className="turn-label">{turn.role === 'user' ? 'You' : 'Hume'}</span>
                <p className="turn-text">{turn.text}</p>
              </div>
            ))}
          </section>
        )}
      </main>

      {/* Hidden audio element — controlled programmatically */}
      <audio ref={audioRef} onEnded={handleAudioEnd} />
    </div>
  )
}
