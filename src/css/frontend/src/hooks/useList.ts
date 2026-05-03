import { useCallback, useState } from 'react'

interface ListItem {
  id: string | number
  [key: string]: unknown
}

interface ListOperations<T extends ListItem> {
  addItem: (item: T) => void
  removeItem: (id: string | number) => void
  updateItem: (id: string | number, newItemData: Partial<T>) => void
  reorderItems: (startIndex: number, endIndex: number) => void
}

type UseListReturn<T extends ListItem> = [T[], ListOperations<T>]

/**
 * Hook to manage a list of items with common operations
 *
 * Use for:
 * - Favorites/pinning system (T076)
 * - Drag-to-reorder lists
 * - Badge counts management (T077, T099)
 * - Any array state with add/remove/update/reorder
 *
 * @template T - Item type (must have `id` property)
 * @param initialItems - Initial array of items
 * @returns [items, operations] where operations = { addItem, removeItem, updateItem, reorderItems }
 *
 * @example
 * const [favorites, { addItem, removeItem }] = useList([])
 * addItem({ id: 'iocs', label: 'IOCs' })
 * removeItem('iocs')
 */
export function useList<T extends ListItem>(initialItems: T[] = []): UseListReturn<T> {
  const [items, setItems] = useState<T[]>(initialItems)

  const addItem = useCallback((item: T): void => {
    setItems((prevItems) => [...prevItems, item])
  }, [])

  const removeItem = useCallback((id: string | number): void => {
    setItems((prevItems) => prevItems.filter((item) => item.id !== id))
  }, [])

  const updateItem = useCallback((id: string | number, newItemData: Partial<T>): void => {
    setItems((prevItems) =>
      prevItems.map((item) => (item.id === id ? { ...item, ...newItemData } : item))
    )
  }, [])

  const reorderItems = useCallback((startIndex: number, endIndex: number): void => {
    setItems((prevItems) => {
      const result = [...prevItems]
      const [removed] = result.splice(startIndex, 1)
      result.splice(endIndex, 0, removed)
      return result
    })
  }, [])

  return [items, { addItem, removeItem, updateItem, reorderItems }]
}

export default useList
