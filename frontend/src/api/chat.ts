// All requests go to /chat/* which Vite proxies to the backend in dev.
// In production, point VITE_API_BASE at your backend host.
const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? ''

export interface VoiceResult {
  audioBlob: Blob
  sessionId: string
  transcript: string
  reply: string
}

export async function sendVoiceMessage(
  audio: Blob,
  sessionId: string | null,
): Promise<VoiceResult> {
  const form = new FormData()
  // Give the blob a filename so the backend can infer the MIME type
  form.append('audio', audio, 'audio.webm')
  if (sessionId) form.append('session_id', sessionId)

  const res = await fetch(`${API_BASE}/chat/voice`, {
    method: 'POST',
    body: form,
    // Do NOT set Content-Type manually — browser must set the multipart boundary
  })

  if (!res.ok) {
    // Try to parse a FastAPI error detail; fall back to status text
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `Server error ${res.status}`)
  }

  const audioBlob = await res.blob()

  // Custom headers must be listed in expose_headers on the backend
  const sessionIdOut = res.headers.get('X-Session-Id') ?? ''
  const transcript = decodeURIComponent(res.headers.get('X-Transcript') ?? '')
  const reply = decodeURIComponent(res.headers.get('X-Reply') ?? '')

  return { audioBlob, sessionId: sessionIdOut, transcript, reply }
}
