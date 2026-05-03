import { useCallback, useEffect, useState } from 'react'
import type { Dispatch, SetStateAction } from 'react'

interface StorageInterface {
  getItem: (key: string) => string | null
  setItem: (key: string, value: string) => void
  removeItem: (key: string) => void
}

type UseStorageReturnType<T> = [T, Dispatch<SetStateAction<T>>, () => void]

/**
 * Generic hook for persisting state in web storage (localStorage or sessionStorage)
 *
 * Use for:
 * - Simple key-value pairs (favorites, search history, panel sizes)
 * - User preferences
 *
 * Notes:
 * - For large state machines, prefer Zustand (already used in uiStore)
 * - useLocalStorage is simpler for lightweight state
 * - Handles JSON serialization automatically
 *
 * @template T - Type of the stored value
 * @param key - Storage key
 * @param defaultValue - Default value if key doesn't exist
 * @param storage - Storage object (localStorage or sessionStorage)
 * @returns [value, setValue, remove]
 */
export const useStorage = <T>(
  key: string,
  defaultValue: T,
  storage: StorageInterface
): UseStorageReturnType<T> => {
  const [value, setValue] = useState<T>(() => {
    const item = storage.getItem(key)
    if (item !== null) {
      try {
        return JSON.parse(item) as T
      } catch {
        // Invalid JSON, use default
        return defaultValue
      }
    }
    return defaultValue
  })

  // Sync state to storage whenever value changes
  useEffect(() => {
    if (value === undefined) {
      storage.removeItem(key)
      return
    }
    try {
      storage.setItem(key, JSON.stringify(value))
    } catch (e) {
      console.warn(`Failed to persist ${key} to storage:`, e)
    }
  }, [key, value, storage])

  const remove = useCallback(() => {
    setValue(undefined as unknown as T)
  }, [])

  return [value, setValue, remove]
}

/**
 * Persist state in localStorage
 *
 * @example
 * const [favorites, setFavorites, removeFavorites] = useLocalStorage('favorites', [])
 * setFavorites([...favorites, 'iocs'])
 * removeFavorites() // Clears from localStorage
 */
export const useLocalStorage = <T>(
  key: string,
  defaultValue: T
): UseStorageReturnType<T> => {
  return useStorage<T>(key, defaultValue, window.localStorage)
}

/**
 * Persist state in sessionStorage
 *
 * Useful for temporary user session data that shouldn't persist across browser close
 */
export const useSessionStorage = <T>(
  key: string,
  defaultValue: T
): UseStorageReturnType<T> => {
  return useStorage<T>(key, defaultValue, window.sessionStorage)
}

export default { useStorage, useLocalStorage, useSessionStorage }
