// TypeScript IDE Helper - Reference all test types
// This file ensures VS Code's TypeScript server picks up test library types
import type { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import type { render, fireEvent, screen, waitFor } from '@testing-library/react'
import type { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type * as _ExecutionTimeline from '@/components/workers/ExecutionTimeline'

// This file is not executed, it's only used by TypeScript for type resolution
