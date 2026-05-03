import { test, expect } from '@playwright/test'

test.describe('Encoding utilities', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('base64 encode/decode roundtrip', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const encoding = await import('../src/utils/encoding')
      const { base64Encode, base64Decode } = encoding
      const original = 'Hello, World!'
      const encoded = base64Encode(original)
      const decoded = base64Decode(encoded)
      const decodedStr = new TextDecoder().decode(decoded)
      return { original, encoded, decoded: decodedStr }
    })

    expect(result.original).toBe('Hello, World!')
    expect(result.decoded).toBe('Hello, World!')
    expect(result.encoded).toBeTruthy()
  })

  test('hex encode/decode roundtrip', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const encoding = await import('../src/utils/encoding')
      const { ab2hex, hex2ab } = encoding
      const original = new Uint8Array([72, 101, 108, 108, 111]) // "Hello"
      const hex = ab2hex(original)
      const decoded = hex2ab(hex)
      return {
        originalLength: original.length,
        hex,
        decodedLength: decoded.length,
        match: original.every((v, i) => v === decoded[i]),
      }
    })

    expect(result.match).toBe(true)
    expect(result.originalLength).toBe(result.decodedLength)
  })

  test('URL-safe base64 encoding', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const encoding = await import('../src/utils/encoding')
      const { base64UrlEncode, base64UrlDecode } = encoding
      const original = 'Test?data+with/special=chars'
      const encoded = base64UrlEncode(original)
      const decoded = base64UrlDecode(encoded)
      const decodedStr = new TextDecoder().decode(decoded)
      return { original, encoded, decoded: decodedStr, noSpecialChars: !encoded.includes('+') }
    })

    expect(result.original).toBe(result.decoded)
    expect(result.noSpecialChars).toBe(true)
  })

  test('URL safe encode/decode', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const encoding = await import('../src/utils/encoding')
      const { encodeURLSafe, decodeURLSafe } = encoding
      const original = 'Hello World & Foo=Bar'
      const encoded = encodeURLSafe(original)
      const decoded = decodeURLSafe(encoded)
      return { original, encoded, decoded }
    })

    expect(result.original).toBe(result.decoded)
    expect(result.encoded).not.toContain(' ')
  })

  test('string to uint8 and back', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const encoding = await import('../src/utils/encoding')
      const { stringToUint8, uint8ToString } = encoding
      const original = 'CyberSecSuite'
      const bytes = stringToUint8(original)
      const decoded = uint8ToString(bytes)
      return { original, decoded, bytesLength: bytes.length }
    })

    expect(result.original).toBe(result.decoded)
    expect(result.bytesLength).toBeGreaterThan(0)
  })

  test('encodeByFormat function', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const encoding = await import('../src/utils/encoding')
      const { encodeByFormat } = encoding
      const original = 'Test'
      return {
        base64: encodeByFormat(original, 'base64'),
        base64url: encodeByFormat(original, 'base64url'),
        hex: encodeByFormat(original, 'hex'),
        utf8: encodeByFormat(original, 'utf8'),
      }
    })

    expect(result.base64).toBeTruthy()
    expect(result.base64url).toBeTruthy()
    expect(result.hex).toBeTruthy()
    expect(result.utf8).toBe('Test')
  })

  test('decodeByFormat function', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const encoding = await import('../src/utils/encoding')
      const { encodeByFormat, decodeByFormat } = encoding
      const original = 'Test Data'

      const b64 = encodeByFormat(original, 'base64')
      const b64url = encodeByFormat(original, 'base64url')
      const hex = encodeByFormat(original, 'hex')

      const fromB64 = new TextDecoder().decode(decodeByFormat(b64, 'base64'))
      const fromB64url = new TextDecoder().decode(decodeByFormat(b64url, 'base64url'))
      const fromHex = new TextDecoder().decode(decodeByFormat(hex, 'hex'))

      return { fromB64, fromB64url, fromHex, original }
    })

    expect(result.fromB64).toBe('Test Data')
    expect(result.fromB64url).toBe('Test Data')
    expect(result.fromHex).toBe('Test Data')
  })
})
