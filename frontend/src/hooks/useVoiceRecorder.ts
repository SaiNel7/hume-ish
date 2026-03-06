import { useRef } from 'react'

export interface VoiceRecorder {
  start: () => Promise<void>   // throws if mic permission denied
  stop: () => Promise<Blob>    // resolves with the recorded audio blob
}

export function useVoiceRecorder(): VoiceRecorder {
  const recorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])

  const start = async (): Promise<void> => {
    // getUserMedia throws NotAllowedError if the user denies permission —
    // let the caller catch it and show an appropriate toast.
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    const recorder = new MediaRecorder(stream)
    recorderRef.current = recorder
    chunksRef.current = []

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data)
    }

    recorder.start()
  }

  const stop = (): Promise<Blob> =>
    new Promise((resolve, reject) => {
      const recorder = recorderRef.current
      if (!recorder) {
        reject(new Error('Recorder not started'))
        return
      }

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType })
        // Release the microphone immediately after recording stops
        recorder.stream.getTracks().forEach((t) => t.stop())
        resolve(blob)
      }

      recorder.stop()
    })

  return { start, stop }
}
