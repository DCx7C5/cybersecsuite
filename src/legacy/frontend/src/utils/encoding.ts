/**
 * Encoding utilities for CyberSecSuite frontend
 * Provides base64, hex, and URL encoding/decoding functions
 */

/**
 * Encode bytes to base64 string
 */
export function base64Encode(data: Uint8Array | string): string {
  const bytes = typeof data === 'string' ? new TextEncoder().encode(data) : data
  let binary = ''
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return btoa(binary)
}

/**
 * Decode base64 string to bytes
 */
export function base64Decode(str: string): Uint8Array {
  const binary = atob(str)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }
  return bytes
}

/**
 * URL-safe base64 encoding (RFC 4648)
 */
export function base64UrlEncode(data: Uint8Array | string): string {
  const b64 = base64Encode(data)
  return b64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
}

/**
 * URL-safe base64 decoding (RFC 4648)
 */
export function base64UrlDecode(str: string): Uint8Array {
  let padded = str.replace(/-/g, '+').replace(/_/g, '/')
  padded += '='.repeat((4 - (padded.length % 4)) % 4)
  return base64Decode(padded)
}

/**
 * Encode bytes to hexadecimal string
 */
export function ab2hex(buffer: Uint8Array | ArrayBuffer): string {
  if (buffer instanceof ArrayBuffer) {
    buffer = new Uint8Array(buffer)
  }
  return Array.from(buffer).map((b) => b.toString(16).padStart(2, '0')).join('')
}

/**
 * Decode hexadecimal string to bytes
 */
export function hex2ab(hex: string): Uint8Array {
  const bytes = new Uint8Array(hex.length / 2)
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substr(i, 2), 16)
  }
  return bytes
}

/**
 * Encode string to URL-safe format
 */
export function encodeURLSafe(str: string): string {
  return encodeURIComponent(str)
}

/**
 * Decode URL-safe string
 */
export function decodeURLSafe(str: string): string {
  return decodeURIComponent(str)
}

/**
 * Convert Uint8Array to readable string (handles UTF-8)
 */
export function uint8ToString(bytes: Uint8Array): string {
  return new TextDecoder().decode(bytes)
}

/**
 * Convert string to Uint8Array (UTF-8)
 */
export function stringToUint8(str: string): Uint8Array {
  return new TextEncoder().encode(str)
}

/**
 * Parse encoding format from string and decode accordingly
 */
export function decodeByFormat(
  data: string,
  format: 'base64' | 'base64url' | 'hex' | 'utf8'
): Uint8Array | string {
  switch (format) {
    case 'base64':
      return base64Decode(data)
    case 'base64url':
      return base64UrlDecode(data)
    case 'hex':
      return hex2ab(data)
    case 'utf8':
      return data
    default:
      throw new Error(`Unknown format: ${format}`)
  }
}

/**
 * Encode data to format
 */
export function encodeByFormat(
  data: Uint8Array | string,
  format: 'base64' | 'base64url' | 'hex' | 'utf8'
): string {
  const bytes = typeof data === 'string' ? stringToUint8(data) : data
  switch (format) {
    case 'base64':
      return base64Encode(bytes)
    case 'base64url':
      return base64UrlEncode(bytes)
    case 'hex':
      return ab2hex(bytes)
    case 'utf8':
      return uint8ToString(bytes)
    default:
      throw new Error(`Unknown format: ${format}`)
  }
}
