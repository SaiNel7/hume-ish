import { useRef, useState } from 'react'
import { Toaster, toast } from 'react-hot-toast'
import { sendVoiceMessage } from './api/chat'
import { AIVoiceInput } from './components/ui/ai-voice-input'
import { SparklesCore } from './components/ui/sparkles'
import { GradientText } from './components/ui/gradient-text'
import { useVoiceRecorder } from './hooks/useVoiceRecorder'
import './App.css'

interface Turn {
  role: 'user' | 'hume'
  text: string
}

type AppState = 'idle' | 'recording' | 'thinking' | 'speaking'

export default function App() {
  const [appState, setAppState] = useState<AppState>('idle')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [turns, setTurns] = useState<Turn[]>([])

  const audioRef = useRef<HTMLAudioElement>(null)
  const audioUrlRef = useRef<string | null>(null)
  const recorder = useVoiceRecorder()
  const isRecording = useRef(false)

  const handleStart = async () => {
    if (appState !== 'idle') return
    try {
      await recorder.start()
      isRecording.current = true
      setAppState('recording')
    } catch {
      toast.error('Microphone access denied. Allow it in your browser settings.')
    }
  }

  const handleStop = async (_duration: number) => {
    if (!isRecording.current) return
    isRecording.current = false
    setAppState('thinking')

    const blob = await recorder.stop()

    try {
      const result = await sendVoiceMessage(blob, sessionId)

      setSessionId(result.sessionId)
      setTurns((prev) => [
        ...prev,
        { role: 'user', text: result.transcript },
        { role: 'hume', text: result.reply },
      ])

      if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current)
      const url = URL.createObjectURL(result.audioBlob)
      audioUrlRef.current = url

      if (audioRef.current) {
        audioRef.current.src = url
        setAppState('speaking')
        audioRef.current.play().catch(() => {
          toast('Tap the mic to play the audio response.', { icon: '🔊' })
        })
      }
    } catch (err) {
      setAppState('idle')
      const message = err instanceof Error ? err.message : 'Something went wrong'
      toast.error(message)
    }
  }

  const handleAudioEnd = () => {
    setAppState('idle')
  }

  const statusLabel: Record<AppState, string | null> = {
    idle: null,
    recording: null,  // AIVoiceInput shows "Listening..." itself
    thinking: 'Thinking…',
    speaking: 'Speaking…',
  }

  return (
    <div className="app">
      <SparklesCore
        id="app-sparkles"
        background="transparent"
        minSize={0.6}
        maxSize={1.4}
        particleDensity={80}
        particleColor="#ffffff"
        speed={1}
        className="fixed inset-0 w-full h-full"
      />
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
        <h1 className="app-title">
          David <GradientText className="bg-black text-white">Hume</GradientText>
        </h1>
      </header>

      <main className="app-main">
        <div style={{ pointerEvents: appState === 'thinking' || appState === 'speaking' ? 'none' : 'auto', opacity: appState === 'thinking' || appState === 'speaking' ? 0.5 : 1 }}>
          <AIVoiceInput onStart={handleStart} onStop={handleStop} />
        </div>

        <p className="app-quote">"Beauty in things exists in the mind which contemplates them." </p> 
        {/* <p className="app-quote">"Be a philosopher, but amidst all your philosophy be still a man" </p>  */}

        {statusLabel[appState] && (
          <p className="orb-label">{statusLabel[appState]}</p>
        )}

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

      <audio ref={audioRef} onEnded={handleAudioEnd} />
    </div>
  )
}
