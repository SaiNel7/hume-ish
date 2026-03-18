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

function CornerMenu() {
  const [open, setOpen] = useState(false)

  const links = [
    {
      href: 'https://sainellutla.com',
      label: 'My page',
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="8" r="4" />
          <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" />
        </svg>
      ),
    },
    {
      href: 'https://plato.stanford.edu/entries/hume/',
      label: 'Stanford Encyclopedia',
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
        </svg>
      ),
    },
  ]

  return (
    <div className="corner-menu">
      <button
        className="corner-menu__toggle"
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? 'Close menu' : 'Open menu'}
      >
        <motion.span
          animate={{ rotate: open ? 225 : 45 }}
          transition={{ duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
          style={{ display: 'flex', transformOrigin: 'center' }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
            <line x1="12" y1="2" x2="12" y2="22" />
            <line x1="2" y1="12" x2="22" y2="12" />
          </svg>
        </motion.span>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            className="corner-menu__items"
            initial={{ opacity: 0, scale: 0.85, y: -6 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.85, y: -6 }}
            transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
          >
            {links.map((link, i) => (
              <motion.a
                key={link.href}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="corner-menu__item"
                aria-label={link.label}
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.07, duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
              >
                {link.icon}
              </motion.a>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

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
      <CornerMenu />
    </div>
  )
}
