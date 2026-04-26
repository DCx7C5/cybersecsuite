import { useState } from 'react'
import * as RQ from '@tanstack/react-query'
import Button from '@/components/ui/Button.tsx'
import Modal from '@/components/ui/Modal.tsx'
import Card from '@/components/ui/Card.tsx'

interface BatchOperationsProps {
  projectId: number
  selectedWorkerIds: number[]
  onComplete?: () => void
}

interface BatchResult {
  success_count: number
  failure_count: number
  details: Array<{ worker_id: number; status: 'success' | 'failed'; message: string }>
}

async function performBatchAction(
  projectId: number,
  action: string,
  workerIds: number[]
): Promise<BatchResult> {
  const response = await fetch(`/api/projects/${projectId}/workers/batch/${action}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ worker_ids: workerIds }),
  })
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`)
  return response.json()
}

export default function BatchOperations({ projectId, selectedWorkerIds, onComplete }: BatchOperationsProps) {
  const [showModal, setShowModal] = useState(false)
  const [currentAction, setCurrentAction] = useState<'start' | 'stop' | 'update' | null>(null)
  const [results, setResults] = useState<BatchResult | null>(null)
  const [showResults, setShowResults] = useState(false)

  const startMutation = RQ.useMutation({
    mutationFn: () => performBatchAction(projectId, 'start', selectedWorkerIds),
    onSuccess: (data) => {
      setResults(data)
      setShowResults(true)
      onComplete?.()
    },
  })

  const stopMutation = RQ.useMutation({
    mutationFn: () => performBatchAction(projectId, 'stop', selectedWorkerIds),
    onSuccess: (data) => {
      setResults(data)
      setShowResults(true)
      onComplete?.()
    },
  })

  const updateMutation = RQ.useMutation({
    mutationFn: () => performBatchAction(projectId, 'update', selectedWorkerIds),
    onSuccess: (data) => {
      setResults(data)
      setShowResults(true)
      onComplete?.()
    },
  })

  if (selectedWorkerIds.length === 0) {
    return null
  }

  const handleAction = (action: 'start' | 'stop' | 'update') => {
    setCurrentAction(action)
    setShowModal(true)
  }

  const handleConfirm = () => {
    switch (currentAction) {
      case 'start':
        startMutation.mutate()
        break
      case 'stop':
        stopMutation.mutate()
        break
      case 'update':
        updateMutation.mutate()
        break
    }
    setShowModal(false)
  }

  const isLoading = startMutation.isPending || stopMutation.isPending || updateMutation.isPending

  return (
    <>
      <Card>
        <div style={{ padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontWeight: 600 }}>
              {selectedWorkerIds.length} worker(s) selected
            </span>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <Button
              variant="primary"
              onClick={() => handleAction('start')}
              disabled={isLoading}
            >
              Start All
            </Button>

            <Button
              variant="danger"
              onClick={() => handleAction('stop')}
              disabled={isLoading}
            >
              Stop All
            </Button>

            <Button
              variant="secondary"
              onClick={() => handleAction('update')}
              disabled={isLoading}
            >
              Update Config
            </Button>
          </div>
        </div>

        {/* Progress Bar */}
        {isLoading && (
          <div style={{ padding: '8px 16px' }}>
            <div
              style={{
                height: '4px',
                background: 'var(--surface-2)',
                borderRadius: '2px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  height: '100%',
                  background: 'linear-gradient(90deg, var(--accent) 0%, var(--accent) 50%, transparent 100%)',
                  backgroundSize: '200% 100%',
                  animation: 'loading 1.5s infinite',
                }}
              />
            </div>
          </div>
        )}
      </Card>

      {/* Confirmation Modal */}
      {showModal && (
        <Modal
          open={showModal}
          title={`Confirm: ${currentAction?.toUpperCase()} all workers?`}
          onClose={() => setShowModal(false)}
        >
          <div style={{ padding: '20px' }}>
            <p>
              You are about to <strong>{currentAction}</strong> {selectedWorkerIds.length} worker(s).
            </p>
            <p style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
              This action may take a few moments to complete.
            </p>

            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end', marginTop: '20px' }}>
              <Button
                variant="ghost"
                onClick={() => setShowModal(false)}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handleConfirm}
                disabled={isLoading}
              >
                {isLoading ? 'Processing...' : 'Confirm'}
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Results Modal */}
      {showResults && results && (
        <Modal
          open={showResults}
          title="Batch Operation Results"
          onClose={() => setShowResults(false)}
        >
          <div style={{ padding: '20px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
              <div style={{ background: 'var(--green-glow)', padding: '12px', borderRadius: '4px', borderLeft: '3px solid var(--green)' }}>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Successful
                </div>
                <div style={{ fontSize: '24px', fontWeight: 600 }}>
                  {results.success_count}
                </div>
              </div>

              <div style={{ background: 'var(--red-glow)', padding: '12px', borderRadius: '4px', borderLeft: '3px solid var(--red)' }}>
                <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px' }}>
                  Failed
                </div>
                <div style={{ fontSize: '24px', fontWeight: 600 }}>
                  {results.failure_count}
                </div>
              </div>
            </div>

            {results.details.length > 0 && (
              <div style={{ maxHeight: '300px', overflow: 'auto' }}>
                <h3 style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                  Details
                </h3>
                {results.details.map((detail, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: '8px',
                      background: 'var(--surface-2)',
                      borderRadius: '4px',
                      marginBottom: '4px',
                      fontSize: '12px',
                      borderLeft: `3px solid ${detail.status === 'success' ? 'var(--green)' : 'var(--red)'}`,
                    }}
                  >
                    <div style={{ fontWeight: 600 }}>
                      Worker {detail.worker_id}
                    </div>
                    <div style={{ color: 'var(--text-muted)' }}>
                      {detail.message}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end', marginTop: '20px' }}>
              <Button
                variant="primary"
                onClick={() => setShowResults(false)}
              >
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}

      <style>{`
        @keyframes loading {
          0% {
            background-position: 200% 0;
          }
          100% {
            background-position: -200% 0;
          }
        }
      `}</style>
    </>
  )
}
