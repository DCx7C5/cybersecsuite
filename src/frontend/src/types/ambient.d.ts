// Ambient type declarations for test libraries
// Suppresses TS2307 errors in IDE while maintaining proper module resolution

declare module 'vitest' {
  export * from 'vitest'
}

declare module '@testing-library/react' {
  export * from '@testing-library/react'
}

declare module '@testing-library/jest-dom' {
  export * from '@testing-library/jest-dom'
}

declare module '@tanstack/react-query' {
  export * from '@tanstack/react-query'
}

declare module '@/components/workers/ExecutionTimeline' {
  import type ExecutionTimeline from '@/components/workers/ExecutionTimeline'
  export default ExecutionTimeline
}
