import { useState } from 'react'
import { useApiQuery } from '@/hooks/useApi.ts'
import Button from '@/components/ui/Button.tsx'
import Card from '@/components/ui/Card.tsx'
import Modal from '@/components/ui/Modal.tsx'
import Input from '@/components/ui/Input.tsx'
import Spinner from '@/components/ui/Spinner.tsx'

interface HistoryItem {
  id: number
  action: string
  timestamp: string
  details: Record<string, unknown>
}

interface Bookmark {
  id: number
  name: string
  timestamp: string
  history_id: number
}

interface ExecutionTimelineProps {
  projectId: number
  workerId: number
}

export default function ExecutionTimeline({ projectId, workerId }: ExecutionTimelineProps) {
  const [dateFilter, setDateFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [newBookmarkName, setNewBookmarkName] = useState('')
  const [showBookmarkModal, setShowBookmarkModal] = useState(false)
  const [selectedHistoryId, setSelectedHistoryId] = useState<number | null>(null)

  const { data: history, isLoading: historyLoading } = useApiQuery<HistoryItem[]>(
    ['worker-history', projectId, workerId],
    `/api/projects/${projectId}/workers/${workerId}/history`
  )

  const { data: bookmarks, isLoading: bookmarksLoading } = useApiQuery<Bookmark[]>(
    ['worker-bookmarks', projectId, workerId],
    `/api/projects/${projectId}/workers/${workerId}/bookmarks`
  )

  const handleAddBookmark = async () => {
    if (!newBookmarkName || !selectedHistoryId) return

    try {
      const response = await fetch(
        `/api/projects/${projectId}/workers/${workerId}/bookmarks`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: newBookmarkName, history_id: selectedHistoryId }),
        }
      )
      if (!response.ok) throw new Error('Failed to add bookmark')
      setNewBookmarkName('')
      setShowBookmarkModal(false)
    } catch (err) {
      console.error('Error adding bookmark:', err)
    }
  }

  const handleDeleteBookmark = async (bookmarkId: number) => {
    try {
      const response = await fetch(
        `/api/projects/${projectId}/workers/${workerId}/bookmarks/${bookmarkId}`,
        { method: 'DELETE' }
      )
      if (!response.ok) throw new Error('Failed to delete bookmark')
    } catch (err) {
      console.error('Error deleting bookmark:', err)
    }
  }

  const handleExport = () => {
    const exportData = {
      timeline: history,
      bookmarks,
      timestamp: new Date().toISOString(),
    }
    const dataStr = JSON.stringify(exportData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `timeline-${workerId}-${Date.now()}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  if (historyLoading || bookmarksLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
        <Spinner />
      </div>
    )
  }

  const items = history || []
  const bookmarkMap = new Map(bookmarks?.map(b => [b.history_id, b]) || [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card>
        <div style={{ padding: '16px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '12px' }}>
            <Input
              type="date"
              value={dateFilter}
              onChange={e => setDateFilter(e.target.value)}
              placeholder="Filter by date..."
            />
            <Input
              value={typeFilter}
              onChange={e => setTypeFilter(e.target.value)}
              placeholder="Filter by action type..."
            />
            <div style={{ display: 'flex', gap: '8px' }}>
              <Button variant="secondary" onClick={handleExport}>
                Export JSON
              </Button>
            </div>
          </div>
        </div>

        <div style={{ padding: '20px' }}>
          {items.length === 0 ? (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '40px' }}>
              No history events yet
            </div>
          ) : (
            <div style={{ position: 'relative' }}>
              <div
                style={{
                  position: 'absolute',
                  left: '20px',
                  top: '0',
                  bottom: '0',
                  width: '2px',
                  background: 'var(--border)',
                }}
              />

              {items.map((item, idx) => {
                const bookmark = bookmarkMap.get(item.id)
                return (
                  <div
                    key={item.id}
                    style={{
                      display: 'flex',
                      gap: '16px',
                      marginBottom: '24px',
                      paddingLeft: '60px',
                      position: 'relative',
                    }}
                  >
                    <div
                      style={{
                        position: 'absolute',
                        left: '12px',
                        top: '8px',
                        width: '16px',
                        height: '16px',
                        borderRadius: '50%',
                        background: bookmark ? 'var(--green)' : 'var(--border)',
                        border: '2px solid var(--surface-1)',
                      }}
                    />

                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <div style={{ fontWeight: 600 }}>{item.action}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                          {new Date(item.timestamp).toLocaleString()}
                        </div>
                      </div>

                      {bookmark && (
                        <div style={{ fontSize: '12px', color: 'var(--green)', marginBottom: '8px' }}>
                          📌 Bookmark: {bookmark.name}
                        </div>
                      )}

                      <pre
                        style={{
                          background: 'var(--surface-2)',
                          padding: '8px',
                          borderRadius: '4px',
                          fontSize: '11px',
                          margin: '0',
                          maxHeight: '200px',
                          overflow: 'auto',
                        }}
                      >
                        {JSON.stringify(item.details, null, 2)}
                      </pre>

                      <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                        {!bookmark && (
                          <Button
                            variant="ghost"
                            onClick={() => {
                              setSelectedHistoryId(item.id)
                              setShowBookmarkModal(true)
                            }}
                            style={{ fontSize: '12px', padding: '4px 8px' }}
                          >
                            + Bookmark
                          </Button>
                        )}
                        {bookmark && (
                          <Button
                            variant="danger"
                            onClick={() => handleDeleteBookmark(bookmark.id)}
                            style={{ fontSize: '12px', padding: '4px 8px' }}
                          >
                            Remove Bookmark
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </Card>

      {showBookmarkModal && (
        <Modal
          title="Add Bookmark"
          onClose={() => setShowBookmarkModal(false)}
        >
          <div style={{ padding: '20px' }}>
            <Input
              value={newBookmarkName}
              onChange={e => setNewBookmarkName(e.target.value)}
              placeholder="Bookmark name..."
              onKeyPress={e => {
                if (e.key === 'Enter') handleAddBookmark()
              }}
            />
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end', marginTop: '16px' }}>
              <Button variant="ghost" onClick={() => setShowBookmarkModal(false)}>
                Cancel
              </Button>
              <Button variant="primary" onClick={handleAddBookmark}>
                Add Bookmark
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}
