import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
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
  const PREVIEW_TURNS: Turn[] = import.meta.env.DEV && import.meta.env.VITE_PREVIEW ? [
    { role: 'user', text: 'What did Hume say about causation?' },
    { role: 'hume', text: "Causation, for Hume, is nowt but a habit of the mind, la. We never actually see one thing causing another — we just see 'em following each other, and our brain fills in the rest. Dead simple when you think about it." },
    { role: 'user', text: 'So we can never really know anything causes anything?' },
    { role: 'hume', text: "Spot on, mate. Custom and repetition trick us into expectin' the future to mirror the past. The sun's risen every day, so we assume it'll rise tomorrow — but that's just habit, not logic. Hume called it the problem of induction, and honestly nobody's properly solved it since." },
    { role: 'user', text: 'What did Hume say about causation?' },
    { role: 'hume', text: "Causation, for Hume, is nowt but a habit of the mind, la. We never actually see one thing causing another — we just see 'em following each other, and our brain fills in the rest. Dead simple when you think about it." },
    { role: 'user', text: 'What did Hume say about causation?' },
    { role: 'hume', text: "Causation, for Hume, is nowt but a habit of the mind, la. We never actually see one thing causing another — we just see 'em following each other, and our brain fills in the rest. Dead simple when you think about it." },
    { role: 'user', text: 'What did Hume say about causation?' },
    { role: 'hume', text: "Causation, for Hume, is nowt but a habit of the mind, la. We never actually see one thing causing another — we just see 'em following each other, and our brain fills in the rest. Dead simple when you think about it." },
  ] : []

  const [turns, setTurns] = useState<Turn[]>(PREVIEW_TURNS)

  const audioRef = useRef<HTMLAudioElement>(null)
  const audioUrlRef = useRef<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const recorder = useVoiceRecorder()
  const isRecording = useRef(false)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [turns])

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

  const isActive = turns.length > 0
  const micDisabled = appState === 'thinking' || appState === 'speaking'

  return (
    <div className={`app ${isActive ? 'app--active' : 'app--idle'}`}>
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

      <motion.div
        layout
        className="app-top"
        transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
      >
        <h1 className="app-title">
          David <GradientText className="bg-black text-white">Hume</GradientText>
        </h1>
        <div style={{ pointerEvents: micDisabled ? 'none' : 'auto', opacity: micDisabled ? 0.5 : 1 }}>
          <AIVoiceInput onStart={handleStart} onStop={handleStop} />
        </div>
        {statusLabel[appState] && <p className="orb-label">{statusLabel[appState]}</p>}
        <p className="app-quote">"Beauty in things exists in the mind which contemplates them."</p>
      </motion.div>

      <AnimatePresence>
        {isActive && (
          <motion.div
            className="chat-scroll"
            ref={scrollRef}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2, ease: [0.4, 0, 0.2, 1] }}
          >
            <section className="transcript" aria-label="Conversation">
              {turns.map((turn, i) => (
                <div key={i} className={`turn turn--${turn.role}`}>
                  <span className="turn-label">{turn.role === 'user' ? 'You' : 'Hume'}</span>
                  <p className="turn-text">{turn.text}</p>
                </div>
              ))}
            </section>
          </motion.div>
        )}
      </AnimatePresence>

      <audio ref={audioRef} onEnded={handleAudioEnd} />
    </div>
  )
}
