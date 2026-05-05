import { useState } from 'react'
import { useUIStore } from '@/store/uiStore'
import Button from '@/components/ui/Button'

export default function SendMessagePrompt() {
  const [message, setMessage] = useState('')
  const { setActiveTab } = useUIStore()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim()) return

    // Route to Chat panel with message
    setActiveTab('chat')
    
    // Dispatch custom event with message content
    window.dispatchEvent(
      new CustomEvent('send-message', { detail: { text: message } })
    )
    
    // Clear input
    setMessage('')
  }

  return (
    <form onSubmit={handleSubmit} style={{ padding: '12px' }}>
      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="💬 Send message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          data-test="send-message-input"
          style={{
            flex: 1,
            padding: '8px 12px',
            borderRadius: '6px',
            border: '1px solid var(--border)',
            background: 'var(--bg-elevated)',
            color: 'var(--text-primary)',
            fontSize: '13px',
            outline: 'none',
            transition: 'border-color 0.2s',
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = 'var(--accent)'
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = 'var(--border)'
          }}
        />
        <Button
          variant="primary"
          type="submit"
          disabled={!message.trim()}
          data-test="send-message-button"
          style={{
            padding: '6px 12px',
            fontSize: '12px',
            minWidth: 'fit-content',
          }}
        >
          Send
        </Button>
      </div>
    </form>
  )
}
