import { useState, useRef, useEffect, useCallback } from 'react'
import { fetchApi } from '@/hooks/useApi'
import Button from '@/components/ui/Button'
import Spinner from '@/components/ui/Spinner'

interface Message { role: 'user' | 'assistant'; content: string }
interface ChatModel { id: string; name: string; provider?: string }

export default function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [models, setModels] = useState<ChatModel[]>([])
  const [selectedModel, setSelectedModel] = useState('')
  const esRef = useRef<EventSource | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchApi<{ models?: ChatModel[] }>('/api/chat-models')
      .then(d => {
        const list = d.models ?? []
        setModels(list)
        if (list.length > 0) setSelectedModel(list[0].id)
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const stop = useCallback(() => {
    esRef.current?.close()
    esRef.current = null
    setIsStreaming(false)
  }, [])

  const send = useCallback(async () => {
    if (!input.trim() || isStreaming) return
    const prompt = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: prompt }])
    setIsStreaming(true)

    try {
      const res = await fetchApi<{ task_id?: string; response?: string }>(
        '/api/agent-query',
        { method: 'POST', body: JSON.stringify({ prompt, stream: true, model: selectedModel || undefined }) }
      )

      if (res.task_id) {
        setMessages(prev => [...prev, { role: 'assistant', content: '' }])
        const es = new EventSource(`/sse/agent-run/${res.task_id}`)
        esRef.current = es
        es.addEventListener('token', (e: MessageEvent) => {
          setMessages(prev => {
            const copy = [...prev]
            const last = copy[copy.length - 1]
            if (last.role === 'assistant') copy[copy.length - 1] = { ...last, content: last.content + (e.data as string) }
            return copy
          })
        })
        es.addEventListener('done', () => { stop() })
        es.addEventListener('error', () => { stop() })
        es.onerror = () => { stop() }
      } else if (res.response) {
        setMessages(prev => [...prev, { role: 'assistant', content: res.response! }])
        setIsStreaming(false)
      }
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${String(e)}` }])
      setIsStreaming(false)
    }
  }, [input, isStreaming, selectedModel, stop])

  const exportChat = useCallback(() => {
    const blob = new Blob([JSON.stringify(messages, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'chat.json'; a.click()
    URL.revokeObjectURL(url)
  }, [messages])

  function renderContent(text: string) {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/`([^`]+)`/g, '<code style="background:var(--surface-2);padding:1px 4px;border-radius:3px;font-family:var(--font-mono)">$1</code>')
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 80px)', gap: '8px' }}>
      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
        <select
          value={selectedModel}
          onChange={e => setSelectedModel(e.target.value)}
          style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', color: 'var(--text-primary)', padding: '4px 8px', fontSize: '12px' }}
        >
          {models.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
        </select>
        <Button variant="ghost" style={{ fontSize: '12px', padding: '4px 10px' }} onClick={() => setMessages([])}>Clear</Button>
        <Button variant="ghost" style={{ fontSize: '12px', padding: '4px 10px' }} onClick={exportChat}>Export</Button>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px', padding: '8px 0' }}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: 'var(--text-faint)', padding: '40px' }}>
            Start a conversation with the AI assistant
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
            <div
              style={{
                maxWidth: '80%',
                padding: '10px 14px',
                borderRadius: 'var(--radius-lg)',
                background: msg.role === 'user' ? 'var(--accent-glow)' : 'var(--surface)',
                border: `1px solid ${msg.role === 'user' ? 'var(--accent)' : 'var(--border)'}`,
                color: 'var(--text-primary)',
                fontSize: '13px',
                lineHeight: 1.7,
                fontFamily: msg.role === 'assistant' ? 'var(--font-mono)' : 'var(--font-ui)',
                whiteSpace: 'pre-wrap',
              }}
              dangerouslySetInnerHTML={{ __html: renderContent(msg.content) }}
            />
          </div>
        ))}
        {isStreaming && messages[messages.length - 1]?.content === '' && (
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', padding: '8px' }}>
            <Spinner size={16} />
            <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>Thinking...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div style={{ display: 'flex', gap: '8px' }}>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); void send() } }}
          placeholder="Type a message... (Enter to send, Shift+Enter for newline)"
          style={{
            flex: 1,
            background: 'var(--surface-2)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            color: 'var(--text-primary)',
            fontSize: '13px',
            padding: '8px 12px',
            resize: 'none',
            height: '60px',
            outline: 'none',
            fontFamily: 'var(--font-ui)',
          }}
        />
        {isStreaming
          ? <Button variant="danger" onClick={stop} style={{ height: '60px' }}>Stop</Button>
          : <Button onClick={() => { void send() }} style={{ height: '60px' }}>Send</Button>
        }
      </div>
    </div>
  )
}
