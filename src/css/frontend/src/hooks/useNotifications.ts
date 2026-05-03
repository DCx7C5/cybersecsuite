import { useContext } from 'react'
import { NotificationContext, type NotificationType, type Notification } from '@/context/NotificationContext'

export type { Notification, NotificationType }

export function useNotifications() {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider')
  }

  return {
    notifications: context.notifications,
    success: (message: string, duration?: number) =>
      context.addNotification(message, 'success', duration),
    error: (message: string, duration?: number) =>
      context.addNotification(message, 'error', duration),
    warning: (message: string, duration?: number) =>
      context.addNotification(message, 'warning', duration),
    info: (message: string, duration?: number) =>
      context.addNotification(message, 'info', duration),
    remove: context.removeNotification,
    clearAll: context.clearAll,
  }
}
